
# Rating Component

This component provides a set of radio buttons that allow the user to rate something, typically using stars or other shapes.

## Usage

```html
<daisy-rating name="product-rating" [value]="3" [max]="5" [(ngModel)]="myRating"></daisy-rating>
```

## Inputs

- `name`: `string` - The name attribute for the radio button group. All radio buttons in a group must have the same `name`.
- `value`: `number` - The current rating value. Defaults to `0`.
- `max`: `number` - The maximum rating value (number of stars/shapes). Defaults to `5`.
- `half`: `boolean` - If true, allows for half-star ratings.
- `hidden`: `boolean` - If true, adds a hidden radio button at the start to allow users to clear their rating.
- `size`: `RatingSize | null` - The size of the rating stars/shapes. Can be `xs`, `sm`, `md`, `lg`, or `xl`.
- `colorClass`: `string | null` - Custom class for the color of the stars/shapes (e.g., `bg-orange-400`).
- `customClass`: `string` - Custom classes to add to the rating container.

## Two-way Data Binding

The `daisy-rating` component supports `ngModel` for two-way data binding.

## Example

```typescript
import { Component } from '@angular/core';
import { RatingComponent } from './daisy-ui/rating/rating.component';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RatingComponent, FormsModule],
  template: `
    <div class="flex flex-col gap-4 items-center">
      <daisy-rating name="movie-rating" [value]="4" [max]="5" [(ngModel)]="movieRating" [size]="'lg'" [colorClass]="'bg-yellow-400'"></daisy-rating>
      <p>Movie Rating: {{ movieRating }} stars</p>

      <daisy-rating name="service-rating" [value]="2.5" [max]="5" [(ngModel)]="serviceRating" [half]="true" [hidden]="true" [size]="'md'" [colorClass]="'bg-green-500'"></daisy-rating>
      <p>Service Rating: {{ serviceRating }} stars</p>
    </div>
  `,
})
export class AppComponent {
  movieRating = 4;
  serviceRating = 2.5;
}
```
