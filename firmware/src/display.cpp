#include "display.hpp"
#include "board.hpp"
#include "shift_byte.hpp"
#include <initializer_list>
#include "esp_timer.h"
#include "esp_rom_sys.h"
#include "esp_check.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
namespace {
portMUX_TYPE lock=portMUX_INITIALIZER_UNLOCKED;
Frame pending;
esp_timer_handle_t timer;
void send_segments(uint8_t value){
    shift_segments(value,
        [](int v){gpio_set_level(board::serial_data,v);},
        [](int v){gpio_set_level(board::shift_clock,v);},
        [](int v){gpio_set_level(board::latch_clock,v);},
        [](){esp_rom_delay_us(1);});
}
void scan(void*) {
    static unsigned index=0;
    static Frame visible;
    for(auto pin:board::digits)gpio_set_level(pin,0);
    esp_rom_delay_us(3); // transistor storage-time blanking
    if(index==0){portENTER_CRITICAL(&lock);visible=pending;portEXIT_CRITICAL(&lock);}
    send_segments(visible.digit[index]);
    gpio_set_level(board::digits[index],1);
    index=(index+1)&3;
}
}
void display::init(){
    uint64_t mask=0;
    for(auto pin:board::digits){gpio_set_level(pin,0);mask|=1ULL<<pin;}
    for(auto pin:{board::serial_data,board::shift_clock,board::latch_clock}){
        gpio_set_level(pin,0);mask|=1ULL<<pin;
    }
    gpio_config_t cfg={};cfg.pin_bit_mask=mask;cfg.mode=GPIO_MODE_OUTPUT;
    ESP_ERROR_CHECK(gpio_config(&cfg));
    send_segments(0); // initialize the latch with every digit off
    esp_timer_create_args_t args={};args.callback=scan;args.name="display_scan";
    args.dispatch_method=ESP_TIMER_TASK;args.skip_unhandled_events=true;
    ESP_ERROR_CHECK(esp_timer_create(&args,&timer));
    ESP_ERROR_CHECK(esp_timer_start_periodic(timer,2000));
}
void display::publish(const Frame &frame){
    portENTER_CRITICAL(&lock);pending=frame;portEXIT_CRITICAL(&lock);
}
void display::self_test(){
    for(unsigned digit=0;digit<4;digit++)for(unsigned bit=0;bit<8;bit++){
        Frame f;f.digit[digit]=1U<<bit;publish(f);vTaskDelay(pdMS_TO_TICKS(250));
    }
    publish(Frame{});
}
