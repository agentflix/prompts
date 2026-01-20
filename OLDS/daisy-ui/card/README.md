
# Card Component

This component displays a card.

## Usage

```html
<daisy-card>
  <figure card-figure>
    <img src="https://img.daisyui.com/images/stock/photo-1606107557195-0e29a4b5b4aa.webp" alt="Shoes" />
  </figure>
  <h2 card-title>Card Title</h2>
  <p>A card component has a figure, a body part, and inside body there are title and actions parts</p>
  <div card-actions class="justify-end">
    <button class="btn btn-primary">Buy Now</button>
  </div>
</daisy-card>
```

## Inputs

- `style`: `CardStyle | null` - The style of the card.
- `size`: `CardSize | null` - The size of the card.
- `side`: `'side' | 'responsive' | null` - The layout of the card.
- `imageFull`: `boolean` - Whether the image should be the background.
- `customClass`: `string` - Custom classes to add to the component.

## Content Projection

The card component uses content projection to allow for flexible content.

- `[card-figure]`: Use this attribute on a `<figure>` element to add an image to the card.
- `[card-title]`: Use this attribute on a heading element to add a title to the card.
- `[card-actions]`: Use this attribute on a `<div>` element to add actions to the card.
- Any other content will be projected into the card body.

## Example

```typescript
import { Component } from '@angular/core';
import { CardComponent } from './daisy-ui/card/card.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CardComponent],
  template: `
    <daisy-card [side]="'responsive'">
        <figure card-figure>
            <img src="https://img.daisyui.com/images/stock/photo-1494232410401-ad00d5433cfa.webp" alt="Album"/>
        </figure>
        <h2 card-title>New album is released!</h2>
        <p>Click the button to listen on Spotiwhy app.</p>
        <div card-actions class="justify-end">
            <button class="btn btn-primary">Listen</button>
        </div>
    </daisy-card>
  `,
})
export class AppComponent {}
```
