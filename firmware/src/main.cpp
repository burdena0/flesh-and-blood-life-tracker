#include <algorithm>
#include "buttons.hpp"
#include "display.hpp"
#include "resources.hpp"
#include "esp_check.h"
#include "esp_log.h"
#include "esp_timer.h"
#include "freertos/task.h"
namespace {
uint32_t milliseconds(){return static_cast<uint32_t>(esp_timer_get_time()/1000);}
void game_task(void *arg){
    auto queue=static_cast<QueueHandle_t>(arg);
    Counter counter;counter.s.epoch=milliseconds();
    uint32_t max_queue_ms=0,last_report=milliseconds();
    for(;;){
        InputEvent event;
        if(xQueueReceive(queue,&event,pdMS_TO_TICKS(5))==pdTRUE){
            const auto now=milliseconds();
            max_queue_ms=std::max(max_queue_ms,uint32_t(now-event.at_ms));
            counter.event(event.key,now);
        }
        const auto now=milliseconds();
        auto frame=render(counter,now);
        if(counter.s.screen==Screen::Play&&counter.s.mana_page&&((now/350)&1))
            for(auto &digit:frame.digit)digit&=0x7f;
        display::publish(frame);
        resources::show(counter.s.screen==Screen::Play?counter.s.resource[counter.s.active]:0);
        if(uint32_t(now-last_report)>=60000){
            ESP_LOGI("counter","Max input queue delay: %lu ms; game stack free: %u bytes",
                static_cast<unsigned long>(max_queue_ms),static_cast<unsigned>(uxTaskGetStackHighWaterMark(nullptr)));
            last_report=now;
        }
    }
}
}
extern "C" void app_main(){
    ESP_LOGI("counter","Native ESP-IDF; S3-Zero, CL3641AH + 74HC595, 4 buttons, 3 LEDs");
    buttons::init();display::init();resources::init();
    if(buttons::select_pressed()){
        display::self_test();
        resources::self_test();
        while(buttons::select_pressed())vTaskDelay(pdMS_TO_TICKS(10));
        vTaskDelay(pdMS_TO_TICKS(40));
    }
    auto queue=xQueueCreate(16,sizeof(InputEvent));
    ESP_ERROR_CHECK(queue?ESP_OK:ESP_ERR_NO_MEM);
    ESP_ERROR_CHECK(xTaskCreate(game_task,"game_state",4096,queue,2,nullptr)==pdPASS?ESP_OK:ESP_ERR_NO_MEM);
    buttons::start(queue);
}
