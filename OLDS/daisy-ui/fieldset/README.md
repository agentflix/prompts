
# Fieldset Component

This component is a container for grouping related form elements, similar to the native HTML `<fieldset>` element.

## Usage

```html
<daisy-fieldset [legend]="'Page title'">
  <input type="text" class="input" placeholder="My awesome page" />
  <p class="label">You can edit page title later on from settings</p>
</daisy-fieldset>
```

## Inputs

- `legend`: `string | null` - The title for the fieldset, displayed in a `<legend>` tag.
- `customClass`: `string` - Custom classes to add to the fieldset container.

## Content Projection

The content inside the `<daisy-fieldset>` tags will be projected into the component, allowing you to place any form elements or other content within the fieldset.

## Example

```typescript
import { Component } from '@angular/core';
import { FieldsetComponent } from './daisy-ui/fieldset/fieldset.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [FieldsetComponent],
  template: `
    <daisy-fieldset [legend]="'Login'" customClass="w-xs bg-base-200 border border-base-300 p-4 rounded-box">
      <label class="label">Email</label>
      <input type="email" class="input" placeholder="Email" />
      <label class="label">Password</label>
      <input type="password" class="input" placeholder="Password" />
      <button class="btn btn-neutral mt-4">Login</button>
    </daisy-fieldset>
  `,
})
export class AppComponent {}
```
