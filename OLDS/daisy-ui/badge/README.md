
# Badge Component

This component displays a badge.

## Usage

```html
<daisy-badge [color]="'primary'">
  Primary
</daisy-badge>
```

## Inputs

- `color`: `BadgeColor | null` - The color of the badge.
- `size`: `BadgeSize | null` - The size of the badge.
- `style`: `BadgeStyle | null` - The style of the badge.
- `customClass`: `string` - Custom classes to add to the component.

## Content Projection

The content of the badge is projected into the component using `<ng-content>`.

## Example

```typescript
import { Component } from '@angular/core';
import { BadgeComponent } from './daisy-ui/badge/badge.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [BadgeComponent],
  template: `
    <daisy-badge [color]="'success'" [style]="'outline'">
      Success
    </daisy-badge>
  `,
})
export class AppComponent {}
```
