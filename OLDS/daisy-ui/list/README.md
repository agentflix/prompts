
# List Component

This component provides a vertical layout to display information in rows.

## Usage

```html
<daisy-list>
  <li daisy-list-row>
    <div>Item 1</div>
    <div>Description 1</div>
  </li>
  <li daisy-list-row>
    <div>Item 2</div>
    <div>Description 2</div>
  </li>
</daisy-list>
```

## Inputs

### `daisy-list`

- `customClass`: `string` - Custom classes to add to the `ul` element.

### `daisy-list-row` (Directive)

- No specific inputs. Apply this directive to `<li>` elements to style them as list rows.

## Content Projection

The `daisy-list` component projects its content, which should be `<li>` elements with the `daisy-list-row` directive applied. Each `li` element can contain any content, which will be arranged in a horizontal grid by default.

## Example

```typescript
import { Component } from '@angular/core';
import { ListComponent, ListRowComponent } from './daisy-ui/list/list.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [ListComponent, ListRowComponent],
  template: `
    <div class="w-full max-w-lg">
      <daisy-list customClass="bg-base-100 rounded-box shadow-md">
        <li class="p-4 pb-2 text-xs opacity-60 tracking-wide">Most played songs this week</li>
        <li daisy-list-row>
          <div><img class="size-10 rounded-box" src="https://img.daisyui.com/images/profile/demo/1@94.webp" alt="Tailwind CSS list item" /></div>
          <div>
            <div>Dio Lupa</div>
            <div class="text-xs uppercase font-semibold opacity-60">Remaining Reason</div>
          </div>
          <button class="btn btn-square btn-ghost">
            <svg class="size-[1.2em]" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><g stroke-linejoin="round" stroke-linecap="round" stroke-width="2" fill="none" stroke="currentColor"><path d="M6 3L20 12 6 21 6 3z"></path></g></svg>
          </button>
          <button class="btn btn-square btn-ghost">
            <svg class="size-[1.2em]" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24"><g stroke-linejoin="round" stroke-linecap="round" stroke-width="2" fill="none" stroke="currentColor"><path d="M19 14c1.49-1.46 3-3.21 3-5.5A5.5 5.5 0 0 0 16.5 3c-1.76 0-3 .5-4.5 2-1.5-1.5-2.74-2-4.5-2A5.5 5.5 0 0 0 2 8.5c0 2.3 1.5 4.05 3 5.5l7 7Z"></path></g></svg>
          </button>
        </li>
      </daisy-list>
    </div>
  `,
})
export class AppComponent {}
```
