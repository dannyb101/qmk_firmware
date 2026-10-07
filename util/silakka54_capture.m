#import <Cocoa/Cocoa.h>

static volatile BOOL received = NO;
static int64_t keyCode;
static uint64_t flags;

static CGEventRef capture(CGEventTapProxy proxy, CGEventType type, CGEventRef event, void *context) {
    if (type == kCGEventKeyDown) {
        keyCode = CGEventGetIntegerValueField(event, kCGKeyboardEventKeycode);
        flags = CGEventGetFlags(event);
        received = YES;
    }
    return event;
}

int main(int argc, const char *argv[]) {
    const char *positions[] = {
        "L00","L01","L02","L03","L04","L05","R00","R01","R02","R03","R04","R05",
        "L10","L11","L12","L13","L14","L15","R10","R11","R12","R13","R14","R15",
        "L20","L21","L22","L23","L24","L25","R20","R21","R22","R23","R24","R25",
        "L30","L31","L32","L33","L34","L35","R30","R31","R32","R33","R34","R35",
        "L43","L44","L45","R43","R44","R45"
    };
    CGEventMask mask = CGEventMaskBit(kCGEventKeyDown);
    CFMachPortRef tap = CGEventTapCreate(kCGSessionEventTap, kCGHeadInsertEventTap, kCGEventTapOptionListenOnly, mask, capture, NULL);
    if (!tap) {
        fprintf(stderr, "Accessibility permission is required for Terminal.\n");
        return 1;
    }
    CFRunLoopSourceRef source = CFMachPortCreateRunLoopSource(NULL, tap, 0);
    CFRunLoopAddSource(CFRunLoopGetCurrent(), source, kCFRunLoopCommonModes);
    CGEventTapEnable(tap, true);
    fprintf(stderr, "Layer %s. Press the requested physical key. Hold the layer key for layer 1.\n", argc > 1 ? argv[1] : "0");
    fprintf(stderr, "Output: position macOS_keycode modifier_flags\n");
    for (int index = 0; index < 54; index++) {
        received = NO;
        fprintf(stderr, "%s: ", positions[index]);
        fflush(stderr);
        while (!received) CFRunLoopRunInMode(kCFRunLoopDefaultMode, 0.05, false);
        printf("%lld 0x%llx\n", keyCode, flags);
    }
    return 0;
}