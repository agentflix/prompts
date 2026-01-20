
# Carousel Component

This component displays a carousel of items.

## Usage

```html
<daisy-carousel>
  <daisy-carousel-item>
    <img src="https://img.daisyui.com/images/stock/photo-1559703248-dcaaec9fab78.webp" alt="Carousel slider" />
  </daisy-carousel-item>
  <daisy-carousel-item>
    <img src="https://img.daisyui.com/images/stock/photo-1565098772267-60af42b81ef2.webp" alt="Carousel slider" />
  </daisy-carousel-item>
</daisy-carousel>
```

## Inputs

### `daisy-carousel`

- `snap`: `CarouselSnap` - Determines how items snap into place. Can be `start`, `center`, or `end`. Defaults to `start`.
- `direction`: `CarouselDirection` - The direction of the carousel. Can be `horizontal` or `vertical`. Defaults to `horizontal`.
- `customClass`: `string` - Custom classes to add to the carousel container.

### `daisy-carousel-item`

- No specific inputs. Content is projected.

## Content Projection

The `daisy-carousel` component projects its content, which should be `daisy-carousel-item` components.
The `daisy-carousel-item` component projects its content, which can be any HTML element, typically an `<img>` tag.

## Example

```typescript
import { Component } from '@angular/core';
import { CarouselComponent, CarouselItemComponent } from './daisy-ui/carousel/carousel.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CarouselComponent, CarouselItemComponent],
  template: `
    <daisy-carousel [snap]="'center'" [customClass]="'w-96'">
      <daisy-carousel-item [customClass]="'w-1/2'">
        <img src="https://img.daisyui.com/images/stock/photo-1559703248-dcaaec9fab78.webp" class="w-full" alt="Tailwind CSS slide plugin" />
      </daisy-carousel-item>
      <daisy-carousel-item [customClass]="'w-1/2'">
        <img src="https://img.daisyui.com/images/stock/photo-1565098772267-60af42b81ef2.webp" class="w-full" alt="Tailwind CSS slide plugin" />
      </daisy-carousel-item>
      <daisy-carousel-item [customClass]="'w-1/2'">
        <img src="https://img.daisyui.com/images/stock/photo-1572635148818-ef6fd45eb394.webp" class="w-full" alt="Tailwind CSS slide plugin" />
      </daisy-carousel-item>
    </daisy-carousel>
  `,
})
export class AppComponent {}
```
