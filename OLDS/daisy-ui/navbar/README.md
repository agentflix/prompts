
# Navbar Component

This component displays a navigation bar at the top of the page, with customizable start, center, and end sections.

## Usage

```html
<daisy-navbar>
  <div navbar-start>
    <button class="btn btn-ghost text-xl">daisyUI</button>
  </div>
  <div navbar-center>
    <ul class="menu menu-horizontal px-1">
      <li><a>Item 1</a></li>
      <li><a>Item 2</a></li>
    </ul>
  </div>
  <div navbar-end>
    <button class="btn">Button</button>
  </div>
</daisy-navbar>
```

## Inputs

- `customClass`: `string` - Custom classes to add to the navbar container.

## Content Projection

The navbar component uses content projection for its different sections:

- `[navbar-start]`: Content for the start (left) section of the navbar.
- `[navbar-center]`: Content for the center section of the navbar.
- `[navbar-end]`: Content for the end (right) section of the navbar.

## Example

```typescript
import { Component } from '@angular/core';
import { NavbarComponent } from './daisy-ui/navbar/navbar.component';
import { DropdownComponent } from './daisy-ui/dropdown/dropdown.component';
import { MenuComponent, MenuItemComponent } from './daisy-ui/menu/menu.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [NavbarComponent, DropdownComponent, MenuComponent, MenuItemComponent],
  template: `
    <daisy-navbar customClass="bg-base-100 shadow-sm">
      <div navbar-start>
        <div class="dropdown">
          <div tabindex="0" role="button" class="btn btn-ghost lg:hidden">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h8m-8 6h16" /></svg>
          </div>
          <ul tabindex="-1" class="mt-3 z-1 p-2 shadow menu menu-sm dropdown-content bg-base-100 rounded-box w-52">
            <li daisy-menu-item><a>Item 1</a></li>
            <li daisy-menu-item><a>Item 2</a></li>
            <li daisy-menu-item><a>Item 3</a></li>
          </ul>
        </div>
        <a class="btn btn-ghost text-xl">daisyUI</a>
      </div>
      <div navbar-center class="hidden lg:flex">
        <ul class="menu menu-horizontal px-1">
          <li daisy-menu-item><a>Item 1</a></li>
          <li daisy-menu-item><a>Item 2</a></li>
          <li daisy-menu-item><a>Item 3</a></li>
        </ul>
      </div>
      <div navbar-end>
        <button class="btn">Button</button>
      </div>
    </daisy-navbar>
  `,
})
export class AppComponent {}
```
