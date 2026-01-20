
# Window Mockup Component

This component displays a box that looks like an operating system window, useful for showcasing desktop content.

## Usage

```html
<daisy-mockup-window>
  <p>Hello from inside the window!</p>
</daisy-mockup-window>
```

## Inputs

- `customClass`: `string` - Custom classes to add to the mockup window container.

## Content Projection

The content inside the `<daisy-mockup-window>` tags will be displayed within the window's content area.

## Example

```typescript
import { Component } from '@angular/core';
import { MockupWindowComponent } from './daisy-ui/mockup-window/mockup-window.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [MockupWindowComponent],
  template: `
    <daisy-mockup-window customClass="bg-base-100">
      <div class="p-4">
        <h2 class="text-xl font-bold">My Application</h2>
        <p>This is a simulated application window.</p>
      </div>
    </daisy-mockup-window>
  `,
})
export class AppComponent {}
```
