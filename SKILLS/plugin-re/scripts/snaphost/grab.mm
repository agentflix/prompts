#import <Cocoa/Cocoa.h>
#include <CoreGraphics/CoreGraphics.h>
#include <dlfcn.h>
typedef CGImageRef (*CapFn)(CGRect, uint32_t, uint32_t, uint32_t);
// captura a janela do PRÓPRIO processo (não exige Gravação de Tela); inclui conteúdo OpenGL/Metal
bool grabOwnWindow (void* nsViewHandle, const char* path)
{
    NSView* v = (__bridge NSView*) nsViewHandle;
    NSWindow* w = v.window; if (!w) return false;
    static CapFn fn = (CapFn) dlsym (RTLD_DEFAULT, "CGWindowListCreateImage");
    if (!fn) return false;
    CGImageRef img = fn (CGRectNull, kCGWindowListOptionIncludingWindow, (uint32_t) w.windowNumber,
                         kCGWindowImageBoundsIgnoreFraming | kCGWindowImageNominalResolution);
    if (!img) return false;
    NSBitmapImageRep* rep = [[NSBitmapImageRep alloc] initWithCGImage: img];
    NSData* d = [rep representationUsingType: NSBitmapImageFileTypePNG properties: @{}];
    bool ok = [d writeToFile: [NSString stringWithUTF8String: path] atomically: NO];
    CGImageRelease (img);
    return ok;
}
