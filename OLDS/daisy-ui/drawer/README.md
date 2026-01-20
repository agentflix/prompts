
# Drawer Component

This component provides a responsive sidebar (drawer) that can be opened and closed.

## Usage

```html
<daisy-drawer id="my-drawer" [(isOpen)]="isDrawerOpen">
  <div drawer-content>
    <!-- Page content here -->
    <label for="my-drawer" class="btn btn-primary drawer-button">Open drawer</label>
  </div>
  <div drawer-side>
    <ul class="menu p-4 w-80 min-h-full bg-base-200 text-base-content">
      <!-- Sidebar content here -->
      <li><a>Sidebar Item 1</a></li>
      <li><a>Sidebar Item 2</a></li>
    </ul>
  </div>
</daisy-drawer>
```

## Inputs

- `id`: `string` - A unique ID for the drawer. This is required to link the drawer toggle with the drawer.
- `isOpen`: `boolean` - Controls whether the drawer is open or closed. Use `[(isOpen)]` for two-way binding.
- `side`: `DrawerSide` - The side from which the drawer opens. Can be `start` (left) or `end` (right). Defaults to `start`.
- `customClass`: `string` - Custom classes to add to the drawer container.

## Content Projection

The drawer component uses content projection for its main content and sidebar content.

- `[drawer-content]`: Use this attribute on an element to define the main content of the page.
- `[drawer-side]`: Use this attribute on an element to define the content of the sidebar.

## Example

```typescript
import { Component } from '@angular/core';
import { DrawerComponent } from './daisy-ui/drawer/drawer.component';
import { FormsModule } from '@angular/forms';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [DrawerComponent, FormsModule],
  template: `
    <div class="h-56 rounded overflow-hidden">
      <daisy-drawer id="my-drawer-2" [(isOpen)]="isDrawerOpen" [side]="'end'">
        <div drawer-content class="flex flex-col items-center justify-center">
          <label for="my-drawer-2" class="btn btn-primary drawer-button">Open drawer</label>
        </div>
        <div drawer-side>
          <ul class="menu p-4 w-80 min-h-full bg-base-200 text-base-content">
            <li><a>Sidebar Item 1</a></li>
            <li><a>Sidebar Item 2</a></li>
          </ul>
        </div>
      </daisy-drawer>
    </div>
  `,
})
export class AppComponent {
  isDrawerOpen = false;
}
```
