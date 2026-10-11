#include <cassert>
#include <cstdint>
#include <cstdio>
#include "../src/shift_byte.hpp"
int main(){
    // Model rising-edge hardware behavior independently of the serializer.
    uint8_t shift=0xa5, output=0x5a;
    int serial=0,clock=0,latch=0;
    for(unsigned value=0;value<256;++value){
        int clocks=0,latches=0;
        const auto previous=output;
        shift_segments(static_cast<uint8_t>(value),
            [&](int v){serial=v;},
            [&](int v){
                if(v&&!clock){shift=uint8_t((shift<<1)|serial);++clocks;}
                assert(output==previous);clock=v;
            },
            [&](int v){if(v&&!latch){output=shift;++latches;}latch=v;},
            [](){});
        assert(clocks==8&&latches==1&&output==value&&clock==0&&latch==0);
    }
    puts("PASS: all 256 segment bytes map to QA..QH with one latch after eight clocks");
}
