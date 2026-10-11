#include "resources.hpp"
#include "board.hpp"
#include "esp_check.h"
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
void resources::init(){
    gpio_config_t cfg={};cfg.mode=GPIO_MODE_OUTPUT;
    for(auto pin:board::resource_leds){gpio_set_level(pin,0);cfg.pin_bit_mask|=1ULL<<pin;}
    ESP_ERROR_CHECK(gpio_config(&cfg));
}
void resources::show(uint8_t count){
    for(unsigned i=0;i<3;++i)gpio_set_level(board::resource_leds[i],i<count);
}
void resources::self_test(){
    for(unsigned i=0;i<3;++i){
        for(unsigned j=0;j<3;++j)gpio_set_level(board::resource_leds[j],i==j);
        vTaskDelay(pdMS_TO_TICKS(300));
    }
    show(0);
}
