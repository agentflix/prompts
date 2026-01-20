
# Footer Component

This component provides a flexible footer layout for your application.

## Usage

```html
<daisy-footer>
  <nav>
    <daisy-footer-title>Services</daisy-footer-title>
    <a class="link link-hover">Branding</a>
    <a class="link link-hover">Design</a>
  </nav>
  <nav>
    <daisy-footer-title>Company</daisy-footer-title>
    <a class="link link-hover">About us</a>
    <a class="link link-hover">Contact</a>
  </nav>
</daisy-footer>
```

## Inputs

### `daisy-footer`

- `direction`: `FooterDirection | null` - Controls the layout direction of the footer sections. Can be `horizontal` or `vertical`. Defaults to `vertical` on small screens and `horizontal` on `sm` and up.
- `center`: `boolean` - If true, aligns the footer content to the center.
- `customClass`: `string` - Custom classes to add to the footer container.

### `daisy-footer-title`

- No specific inputs. Content is projected.

## Content Projection

The `daisy-footer` component projects its content, which typically consists of `<nav>` elements containing `daisy-footer-title` and links.

- `daisy-footer-title`: Use this component to define the title of a footer column.
- Any other content within `<daisy-footer>` will be placed directly inside the footer.

## Example

```typescript
import { Component } from '@angular/core';
import { FooterComponent, FooterTitleComponent } from './daisy-ui/footer/footer.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [FooterComponent, FooterTitleComponent],
  template: `
    <daisy-footer [direction]="'horizontal'" [customClass]="'bg-neutral text-neutral-content rounded'">
      <nav>
        <daisy-footer-title>Services</daisy-footer-title>
        <a class="link link-hover">Branding</a>
        <a class="link link-hover">Design</a>
        <a class="link link-hover">Marketing</a>
        <a class="link link-hover">Advertisement</a>
      </nav>
      <nav>
        <daisy-footer-title>Company</daisy-footer-title>
        <a class="link link-hover">About us</a>
        <a class="link link-hover">Contact</a>
        <a class="link link-hover">Jobs</a>
        <a class="link link-hover">Press kit</a>
      </nav>
      <nav>
        <daisy-footer-title>Legal</daisy-footer-title>
        <a class="link link-hover">Terms of use</a>
        <a class="link link-hover">Privacy policy</a>
        <a class="link link-hover">Cookie policy</a>
      </nav>
    </daisy-footer>
  `,
})
export class AppComponent {}
```
