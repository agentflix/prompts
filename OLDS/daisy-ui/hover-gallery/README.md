
# Hover Gallery Component

This component displays a gallery of images where hovering horizontally reveals other images.

## Usage

```html
<daisy-hover-gallery [images]="imageUrls"></daisy-hover-gallery>
```

## Inputs

- `images`: `string[]` - An array of image URLs to display in the gallery.
- `customClass`: `string` - Custom classes to add to the hover gallery container.

## Example

```typescript
import { Component } from '@angular/core';
import { HoverGalleryComponent } from './daisy-ui/hover-gallery/hover-gallery.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [HoverGalleryComponent],
  template: `
    <daisy-hover-gallery
      [images]="[
        'https://img.daisyui.com/images/stock/daisyui-hat-1.webp',
        'https://img.daisyui.com/images/stock/daisyui-hat-2.webp',
        'https://img.daisyui.com/images/stock/daisyui-hat-3.webp',
        'https://img.daisyui.com/images/stock/daisyui-hat-4.webp'
      ]"
      [customClass]="'max-w-60'"
    ></daisy-hover-gallery>
  `,
})
export class AppComponent {}
```
