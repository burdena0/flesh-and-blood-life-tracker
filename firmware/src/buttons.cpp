#include "buttons.hpp"
#include "board.hpp"
#include "esp_timer.h"
#include "esp_check.h"
#include "esp_log.h"
#include "freertos/task.h"
namespace {
void task(void *arg){
    auto queue=static_cast<QueueHandle_t>(arg);
    Button keys[]={{Key::Minus},{Key::Ok},{Key::Plus},{Key::Resource}};
    TickType_t next=xTaskGetTickCount();
    for(;;){
        const auto now=static_cast<uint32_t>(esp_timer_get_time()/1000);
        for(unsigned i=0;i<4;i++){
            Key key=keys[i].poll(gpio_get_level(board::buttons[i])!=0,now);
            if(key!=Key::None){
                InputEvent event{key,now};
                // Bounded queue; report overflow instead of silently blocking scanning.
                if(xQueueSend(queue,&event,0)!=pdTRUE)ESP_LOGE("buttons","Input queue overflow; event dropped");
            }
        }
        vTaskDelayUntil(&next,pdMS_TO_TICKS(5));
    }
}
}
void buttons::init(){
    gpio_config_t cfg={};
    for(auto pin:board::buttons)cfg.pin_bit_mask|=1ULL<<pin;
    cfg.mode=GPIO_MODE_INPUT; // external 10k pull-ups are fitted on all four inputs
    ESP_ERROR_CHECK(gpio_config(&cfg));
}
bool buttons::select_pressed(){return gpio_get_level(board::buttons[1])==0;}
void buttons::start(QueueHandle_t queue){
    ESP_ERROR_CHECK(xTaskCreate(task,"button_input",3072,queue,3,nullptr)==pdPASS?ESP_OK:ESP_ERR_NO_MEM);
}
