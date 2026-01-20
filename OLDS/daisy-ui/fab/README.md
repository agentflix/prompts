
# FAB (Floating Action Button) Component

This component displays a Floating Action Button (FAB) which can reveal additional "Speed Dial" buttons.

## Usage

```html
<div class="h-54">
  <daisy-fab>
    <div tabindex="0" role="button" class="btn btn-lg btn-circle btn-primary">F</div>
    <button class="btn btn-lg btn-circle">A</button>
    <button class="btn btn-lg btn-circle">B</button>
    <button class="btn btn-lg btn-circle">C</button>
  </daisy-fab>
</div>
```

## Inputs

- `flower`: `boolean` - If true, the speed dial buttons will open in a quarter circle arrangement instead of vertically.
- `customClass`: `string` - Custom classes to add to the FAB container.

## Content Projection

The `daisy-fab` component projects its content. The first focusable element (e.g., `div[tabindex="0"]` or `<button>`) will act as the main FAB button. Subsequent buttons will be the speed dial actions.

- **Main FAB Button**: The first child element that is focusable (e.g., `<div tabindex="0" role="button" class="btn btn-lg btn-circle btn-primary">F</div>`).
- **Speed Dial Buttons**: Subsequent `<button>` elements will appear when the FAB is active.
- **`fab-close`**: An element with the `fab-close` class will replace the main FAB button when the speed dial is open, typically used for a close action.
- **`fab-main-action`**: An element with the `fab-main-action` class will replace the main FAB button when the speed dial is open, typically used for a primary action.

## Example

```typescript
import { Component } from '@angular/core';
import { FabComponent } from './daisy-ui/fab/fab.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [FabComponent],
  template: `
    <div class="h-54">
      <daisy-fab [flower]="true">
        <div tabindex="0" role="button" class="btn btn-lg btn-circle btn-success">F</div>
        <button class="fab-main-action btn btn-circle btn-lg">M</button>
        <button class="btn btn-lg btn-circle">A</button>
        <button class="btn btn-lg btn-circle">B</button>
        <button class="btn btn-lg btn-circle">C</button>
        <button class="btn btn-lg btn-circle">D</button>
      </daisy-fab>
    </div>
  `,
})
export class AppComponent {}
```
