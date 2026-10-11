#include "../life_counter_5641as/counter.hpp"
#include <cassert>
#include <iostream>
int main(){
 Counter c; auto e=[&](Key k){return c.event(k,1000);};
 e(Key::Plus);assert(c.s.start==40);e(Key::Ok);e(Key::Plus);e(Key::Ok);
 assert(c.s.magic&&c.s.life[0]==40&&c.s.life[1]==40);
 e(Key::Minus);e(Key::Ok);e(Key::Plus);assert(c.s.life[0]==39&&c.s.life[1]==41);
 e(Key::Hold);e(Key::Plus);e(Key::Ok);assert(c.s.mana_page);
 e(Key::Plus);assert(c.s.mana[1]==1&&c.s.life[1]==41);
 e(Key::Hold);e(Key::Plus);e(Key::Plus);e(Key::Ok);assert(c.s.mana[1]==0);
 e(Key::Plus);e(Key::Hold);for(int i=0;i<3;i++)e(Key::Plus);e(Key::Ok);
 assert(c.s.screen==Screen::Confirm&&!c.s.yes);e(Key::Ok);assert(c.s.mana[1]==1);
 e(Key::Hold);for(int i=0;i<3;i++)e(Key::Plus);e(Key::Ok);e(Key::Plus);e(Key::Ok);assert(c.s.mana[1]==0);
 e(Key::Hold);for(int i=0;i<2;i++)e(Key::Plus);e(Key::Ok);assert(c.s.mana[1]==1);
 c.s.mana[1]=99;assert(e(Key::Plus)==Haptic::Limit);c.s.mana[1]=0;assert(e(Key::Minus)==Haptic::Limit);
 c.s.mana_page=false;c.s.life[1]=999;assert(e(Key::Plus)==Haptic::Limit);
 c.s.life[1]=-99;assert(e(Key::Minus)==Haptic::Limit);
 c.s.life[1]=-1;c.s.epoch=0;Frame neg=render(c,800);assert(neg.digit[1]==rotate180(glyph('-')));
 c.s.life[1]=123;Frame large=render(c,800);assert(large.digit[0]==rotate180(glyph('3')|0x80));
 Frame f=pair_values(12,34,0,true);assert(f.digit[0]==6&&f.digit[1]==(0x5b|0x80));
 assert(f.digit[2]==rotate180(0x66)&&f.digit[3]==rotate180(0x4f));
 for(int i=0;i<256;i++)assert(rotate180(rotate180(i))==i);
 Frame original=f;flip(f);flip(f);assert(memcmp(f.digit,original.digit,4)==0);
 e(Key::Hold);for(int i=0;i<4;i++)e(Key::Plus);e(Key::Ok);e(Key::Plus);e(Key::Ok);assert(c.s.screen==Screen::Start);
 Button b{Key::Ok};assert(b.poll(false,10)==Key::None);assert(b.poll(true,15)==Key::None);
 b.poll(false,20);b.poll(false,50);assert(b.poll(false,1250)==Key::Hold);
 b.poll(true,1260);assert(b.poll(true,1290)==Key::None);
 Button wrap{Key::Minus};wrap.poll(false,0xfffffff0);wrap.poll(false,20);wrap.poll(true,30);assert(wrap.poll(true,60)==Key::Minus);
 Counter r;assert(r.event(Key::Resource,0)==Haptic::None);
 r.event(Key::Ok,0);assert(r.event(Key::Resource,0)==Haptic::None);r.event(Key::Ok,0);
 for(int i=1;i<=4;i++){r.event(Key::Resource,0);assert(r.s.resource[0]==i%4&&r.s.resource[1]==0);}
 r.event(Key::Ok,0);r.event(Key::Resource,0);assert(r.s.resource[0]==0&&r.s.resource[1]==1);
 r.event(Key::Minus,0);r.event(Key::Hold,0);r.event(Key::Plus,0);r.event(Key::Ok,0);
 assert(r.s.life[1]==20&&r.s.resource[1]==1);
 r.event(Key::Hold,0);assert(r.event(Key::Resource,0)==Haptic::None);
 r.event(Key::Plus,0);r.event(Key::Ok,0);assert(r.s.resource[1]==0&&r.s.life[1]==20);
 // Undo the previous player's wrap, restoring both selection and resource value.
 r.event(Key::Hold,0);r.event(Key::Plus,0);r.event(Key::Ok,0);assert(r.s.active==0&&r.s.resource[0]==3);
 r.event(Key::Hold,0);r.event(Key::Plus,0);r.event(Key::Plus,0);r.event(Key::Ok,0);
 r.event(Key::Plus,0);r.event(Key::Ok,0);r.event(Key::Ok,0);r.event(Key::Ok,0);
 assert(r.s.resource[0]==0&&r.s.resource[1]==0);
 Button rb{Key::Resource};rb.poll(false,0);rb.poll(false,35);assert(rb.poll(false,2000)==Key::None);
 rb.poll(true,2010);assert(rb.poll(true,2040)==Key::Resource);
 std::cout<<"PASS: startup, player edits, mana isolation, undo, confirmations, bounds, 180-degree mapping, debounce, timer wrap, per-player resource cycle/undo/reset, resource button release\n";
}

