
# Dropdown Component

This component displays a dropdown menu or content. It uses the CSS focus method for toggling.

## Usage

```html
<daisy-dropdown [placement]="['bottom', 'end']">
  <div dropdown-trigger>Click</div>
  <ul dropdown-content>
    <li><a>Item 1</a></li>
    <li><a>Item 2</a></li>
  </ul>
</daisy-dropdown>
```

## Inputs

- `placement`: `DropdownPlacement[]` - An array of strings to control the placement of the dropdown content relative to the trigger. Can include `start`, `center`, `end`, `top`, `bottom`, `left`, `right`.
- `hover`: `boolean` - If true, the dropdown opens on hover.
- `open`: `boolean` - Forces the dropdown to be open.
- `customClass`: `string` - Custom classes to add to the dropdown container.
- `contentCustomClass`: `string` - Custom classes to add to the dropdown content container.
- `triggerCustomClass`: `string` - Custom classes to add to the dropdown trigger button.

## Content Projection

The dropdown component uses content projection for its trigger and content.

- `[dropdown-trigger]`: Use this attribute on an element (e.g., a `<div>` or `<button>`) to define the element that triggers the dropdown.
- `[dropdown-content]`: Use this attribute on an element (e.g., a `<ul>` or `<div>`) to define the content that appears in the dropdown.

## Example

```typescript
import { Component } from '@angular/core';
import { DropdownComponent } from './daisy-ui/dropdown/dropdown.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [DropdownComponent],
  template: `
    <daisy-dropdown [placement]="['bottom', 'end']" [hover]="true">
      <div dropdown-trigger class="btn">Hover me</div>
      <ul dropdown-content class="p-2 shadow-sm menu bg-base-100 rounded-box w-52">
        <li><a>Item 1</a></li>
        <li><a>Item 2</a></li>
      </ul>
    </daisy-dropdown>

    <daisy-dropdown [placement]="['top', 'center']">
      <div dropdown-trigger class="btn">Click me</div>
      <div dropdown-content class="shadow-md card card-sm bg-base-100">
        <div class="card-body">
          <p>This is a card. You can use any element as a dropdown.</p>
        </div>
      </div>
    </daisy-dropdown>
  `,
})
export class AppComponent {}
```
