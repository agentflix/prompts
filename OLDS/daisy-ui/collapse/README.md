
# Collapse Component

This component displays a collapsible content area.

## Usage

```html
<daisy-collapse [icon]="'arrow'">
  <div collapse-title>How do I create an account?</div>
  <div collapse-content>Click the "Sign Up" button in the top right corner and follow the registration process.</div>
</daisy-collapse>
```

## Inputs

- `icon`: `CollapseIcon | null` - Adds an icon to the collapse title. Can be `arrow` or `plus`.
- `open`: `boolean` - Controls whether the collapse is open or closed.
- `checkbox`: `boolean` - If true, uses a checkbox for toggling, otherwise uses focus.
- `customClass`: `string` - Custom classes to add to the component.

## Content Projection

The collapse component uses content projection for its title and content.

- `[collapse-title]`: Use this attribute on an element to define the title of the collapse.
- `[collapse-content]`: Use this attribute on an element to define the content of the collapse.

## Example

```typescript
import { Component } from '@angular/core';
import { CollapseComponent } from './daisy-ui/collapse/collapse.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CollapseComponent],
  template: `
    <daisy-collapse [icon]="'plus'" [checkbox]="true">
      <div collapse-title>How do I create an account?</div>
      <div collapse-content>Click the "Sign Up" button in the top right corner and follow the registration process.</div>
    </daisy-collapse>
  `,
})
export class AppComponent {}
```
