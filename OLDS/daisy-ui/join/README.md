
# Join Component

This component is a container for grouping multiple items (buttons, inputs, etc.) horizontally or vertically. It applies border radius to the first and last item.

## Usage

```html
<daisy-join>
  <button daisyJoinItem class="btn">Button</button>
  <button daisyJoinItem class="btn">Button</button>
  <button daisyJoinItem class="btn">Button</button>
</daisy-join>
```

## Inputs

### `daisy-join`

- `direction`: `JoinDirection | null` - The direction of the items. Can be `horizontal` or `vertical`.
- `customClass`: `string` - Custom classes to add to the join container.

### `daisyJoinItem` (Directive)

- No specific inputs. Apply this directive to any element that should be part of the join group.

## Content Projection

The `daisy-join` component projects its content. Any elements with the `daisyJoinItem` directive applied will be styled as part of the join group.

## Example

```typescript
import { Component } from '@angular/core';
import { JoinComponent, JoinItemDirective } from './daisy-ui/join/join.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [JoinComponent, JoinItemDirective],
  template: `
    <daisy-join [direction]="'horizontal'">
      <button daisyJoinItem class="btn">Button</button>
      <button daisyJoinItem class="btn">Button</button>
      <button daisyJoinItem class="btn">Button</button>
    </daisy-join>

    <div class="join join-vertical lg:join-horizontal">
      <input daisyJoinItem class="input input-bordered" placeholder="Email" />
      <button daisyJoinItem class="btn btn-primary">Subscribe</button>
    </div>
  `,
})
export class AppComponent {}
```
