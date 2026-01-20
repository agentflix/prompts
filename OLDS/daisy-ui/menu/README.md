
# Menu Component

This component displays a list of links vertically or horizontally, with support for submenus, titles, and active/disabled states.

## Usage

```html
<daisy-menu>
  <li daisy-menu-item><a>Item 1</a></li>
  <li daisy-menu-item [active]="true"><a>Item 2</a></li>
  <li daisy-menu-item [disabled]="true"><a>Item 3</a></li>
</daisy-menu>
```

## Components and Inputs

### `daisy-menu`

- `direction`: `MenuDirection` - The direction of the menu. Can be `vertical` or `horizontal`. Defaults to `vertical`.
- `size`: `MenuSize | null` - The size of the menu. Can be `xs`, `sm`, `md`, `lg`, or `xl`.
- `customClass`: `string` - Custom classes to add to the `ul` element.

### `li[daisy-menu-item]`

- `active`: `boolean` - If true, the menu item will be styled as active.
- `disabled`: `boolean` - If true, the menu item will be styled as disabled.
- `isDropdown`: `boolean` - If true, the menu item will be rendered as a collapsible dropdown using `<details>`.
- `dropdownOpen`: `boolean` - Controls the open state of the dropdown when `isDropdown` is true.
- `customClass`: `string` - Custom classes to add to the `<a>` element inside the `li`.

### `li[daisy-menu-title]`

- No specific inputs. Use this to create a title within the menu.

## Content Projection

### `daisy-menu`

Projects `li[daisy-menu-item]` and `li[daisy-menu-title]` elements.

### `li[daisy-menu-item]`

- When `isDropdown` is false: Projects its content directly into an `<a>` tag.
- When `isDropdown` is true:
  - `[menu-summary]`: Projects content into the `<summary>` tag of the `<details>` element.
  - `[menu-dropdown-content]`: Projects content into the `<ul>` element of the dropdown.

## Example

```typescript
import { Component } from '@angular/core';
import { MenuComponent, MenuItemComponent, MenuTitleComponent } from './daisy-ui/menu/menu.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [MenuComponent, MenuItemComponent, MenuTitleComponent],
  template: `
    <daisy-menu customClass="bg-base-200 w-56 rounded-box">
      <li daisy-menu-title>Title</li>
      <li daisy-menu-item><a>Item 1</a></li>
      <li daisy-menu-item [active]="true"><a>Item 2</a></li>
      <li daisy-menu-item [isDropdown]="true" [dropdownOpen]="true">
        <span menu-summary>Parent</span>
        <ul menu-dropdown-content>
          <li daisy-menu-item><a>Submenu 1</a></li>
          <li daisy-menu-item><a>Submenu 2</a></li>
        </ul>
      </li>
      <li daisy-menu-item><a>Item 3</a></li>
    </daisy-menu>

    <daisy-menu [direction]="'horizontal'" customClass="bg-base-200 rounded-box mt-6">
      <li daisy-menu-item><a>Item A</a></li>
      <li daisy-menu-item><a>Item B</a></li>
      <li daisy-menu-item><a>Item C</a></li>
    </daisy-menu>
  `,
})
export class AppComponent {}
```
