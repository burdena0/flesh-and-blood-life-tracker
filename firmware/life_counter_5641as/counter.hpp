#pragma once
#include <stdint.h>
#include <stdio.h>
#include <string.h>

enum class Key:uint8_t { None,Minus,Plus,Ok,Hold,Resource };
enum class Screen:uint8_t { Start,Magic,Play,Menu,Confirm };
enum class Action:uint8_t { Resume,Page,Undo,Clear,Reset };
enum class Haptic:uint8_t { None,Click,Select,Confirm,Limit };
struct State {
    Screen screen=Screen::Start;
    int life[2]={20,20}; int mana[2]={0,0}; uint8_t resource[2]={0,0};
    int start=20; uint8_t active=0,menu=0;
    bool magic=false,mana_page=false,yes=false;
    Action confirm_action=Action::Reset;
    uint32_t epoch=0;
};
struct History {int a,b;uint8_t active;bool mana;uint8_t r0,r1;bool resource;};
class Counter {
    History history[100];int count=0;
    void push(bool mana,bool resource=false) {
        if(count==100){memmove(history,history+1,99*sizeof(History));--count;}
        int *p=mana?s.mana:s.life;history[count++]={p[0],p[1],s.active,mana,s.resource[0],s.resource[1],resource};
    }
public:
    State s;
    Action menu_action() const {
        static const Action basic[]={Action::Resume,Action::Undo,Action::Reset};
        static const Action magic[]={Action::Resume,Action::Page,Action::Undo,Action::Clear,Action::Reset};
        return s.magic?magic[s.menu]:basic[s.menu];
    }
    Haptic event(Key key,uint32_t now) {
        if(key==Key::None)return Haptic::None;
        if(key==Key::Resource){
            if(s.screen!=Screen::Play)return Haptic::None;
            push(s.mana_page,true);
            s.resource[s.active]=(s.resource[s.active]+1)%4;
            return Haptic::Click;
        }
        bool edit=key==Key::Minus||key==Key::Plus;
        int delta=key==Key::Plus?1:-1;
        Haptic result=Haptic::Click;
        Screen before=s.screen;uint8_t oldplayer=s.active;bool oldpage=s.mana_page;
        switch(s.screen) {
        case Screen::Start:
            if(edit)s.start=s.start==20?40:20;
            else if(key==Key::Ok){s.life[0]=s.life[1]=s.start;s.screen=Screen::Magic;result=Haptic::Select;}
            else return Haptic::None;
            break;
        case Screen::Magic:
            if(edit)s.magic=!s.magic;
            else if(key==Key::Ok){s.mana[0]=s.mana[1]=0;s.resource[0]=s.resource[1]=0;s.active=0;s.mana_page=false;count=0;s.screen=Screen::Play;result=Haptic::Confirm;}
            else return Haptic::None;
            break;
        case Screen::Play:
            if(edit){
                int *p=s.mana_page?s.mana:s.life;int max=s.mana_page?99:999;
                int value=p[s.active]+delta;
                if(value<(s.mana_page?0:-99)||value>max)return Haptic::Limit;
                push(s.mana_page);p[s.active]=value;
            }else if(key==Key::Ok){s.active^=1;result=Haptic::Select;}
            else if(key==Key::Hold){s.menu=0;s.screen=Screen::Menu;result=Haptic::Select;}
            break;
        case Screen::Menu:
            if(edit){int n=s.magic?5:3;s.menu=(s.menu+n+delta)%n;}
            else if(key==Key::Ok){
                Action a=menu_action();
                if(a==Action::Resume)s.screen=Screen::Play;
                else if(a==Action::Page){s.mana_page=!s.mana_page;s.screen=Screen::Play;}
                else if(a==Action::Undo){
                    if(count){auto h=history[--count];
                        if(h.resource){s.resource[0]=h.r0;s.resource[1]=h.r1;}
                        else{int *p=h.mana?s.mana:s.life;p[0]=h.a;p[1]=h.b;}
                        s.active=h.active;s.mana_page=h.mana;
                    }
                    else result=Haptic::Limit;
                    s.screen=Screen::Play;
                }else{s.confirm_action=a;s.yes=false;s.screen=Screen::Confirm;}
            }else return Haptic::None;
            break;
        case Screen::Confirm:
            if(edit)s.yes=!s.yes;
            else if(key==Key::Ok){
                s.screen=Screen::Play;
                if(s.yes){
                    if(s.confirm_action==Action::Reset){s.screen=Screen::Start;count=0;}
                    else{push(true);s.mana[0]=s.mana[1]=0;}
                    result=Haptic::Confirm;
                }
            }else return Haptic::None;
            break;
        }
        if(before!=s.screen||oldplayer!=s.active||oldpage!=s.mana_page)s.epoch=now;
        return result;
    }
};

struct Button {
    Key key; bool raw=true,stable=true,held=false;
    uint32_t changed=0,pressed=0;
    Key poll(bool high,uint32_t now) {
        if(high!=raw){raw=high;changed=now;}
        if(stable!=raw&&uint32_t(now-changed)>=30){
            stable=raw;
            if(!stable){pressed=now;held=false;}
            else if(!held)return key;
        }
        if(!stable&&key==Key::Ok&&!held&&uint32_t(now-pressed)>=1200){held=true;return Key::Hold;}
        return Key::None;
    }
};

struct Frame {uint8_t digit[4]={0,0,0,0};bool colon=false;};
static constexpr uint8_t digits[]={0x3f,6,0x5b,0x4f,0x66,0x6d,0x7d,7,0x7f,0x6f};
inline uint8_t glyph(char c){
    if(c>='0'&&c<='9')return digits[c-'0'];
    switch(c){case 'L':return 0x38;case 'I':return 6;case 'F':return 0x71;case 'E':return 0x79;
    case 'n':return 0x54;case 'A':return 0x77;case 'o':return 0x5c;case 'P':return 0x73;
    case 'Y':return 0x6e;case 'U':return 0x3e;case 'd':return 0x5e;case 'C':return 0x39;
    case 'r':return 0x50;case 'S':return 0x6d;case 't':return 0x78;case '-':return 0x40;default:return 0;}
}
inline uint8_t rotate180(uint8_t v){return ((v&7)<<3)|((v&0x38)>>3)|(v&0xc0);}
inline Frame word(const char *s){Frame f;for(int i=0;i<4&&s[i];++i)f.digit[i]=glyph(s[i]);return f;}
inline void flip(Frame &f){for(int i=0;i<2;i++){uint8_t t=f.digit[i];f.digit[i]=rotate180(f.digit[3-i]);f.digit[3-i]=rotate180(t);}}
inline Frame pair_values(int a,int b,uint8_t active,bool colon){
    Frame f;f.digit[0]=digits[a/10];f.digit[1]=digits[a%10];
    f.digit[2]=rotate180(digits[b%10]);f.digit[3]=rotate180(digits[b/10]);
    f.digit[active?3:1]|=0x80;f.colon=colon;return f;
}
inline Frame render(const Counter &c,uint32_t now){
    auto &s=c.s;uint32_t phase=uint32_t(now-s.epoch);
    if(s.screen==Screen::Start){if(phase<650)return word("LIFE");return pair_values(s.start,s.start,0,true);}
    if(s.screen==Screen::Magic){if(phase<650)return word("nAnA");return word(s.magic?"on  ":"no  ");}
    if(s.screen==Screen::Menu){
        Frame f;
        switch(c.menu_action()){
        case Action::Resume:f=word("PLAY");break;case Action::Page:f=word(s.mana_page?"LIFE":"nAnA");break;
        case Action::Undo:f=word("Undo");break;case Action::Clear:f=word("CLr ");break;case Action::Reset:f=word("rSt ");break;}
        if(s.active)flip(f);
        return f;
    }
    if(s.screen==Screen::Confirm){Frame f=word(s.yes?"YES ":"no  ");if(s.active)flip(f);return f;}
    const int *p=s.mana_page?s.mana:s.life;
    if(s.mana_page&&phase<650){Frame f=word("nAnA");if(s.active)flip(f);return f;}
    if(p[0]>=0&&p[1]>=0&&p[0]<=99&&p[1]<=99)return pair_values(p[0],p[1],s.active,!s.mana_page);
    // Three-digit life: alternate full-display player label and value, without truncation.
    int player=(phase%3200)<1600?s.active:1-s.active;char buf[8];
    if(phase%1600<650)snprintf(buf,sizeof(buf),"P%d  ",player+1);
    else snprintf(buf,sizeof(buf),"%4d",p[player]);
    Frame f=word(buf);if(player==s.active)f.digit[3]|=0x80;if(player)flip(f);return f;
}
