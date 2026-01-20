
# Phone Mockup Component

This component displays a mockup of an iPhone, useful for showcasing mobile content.

## Usage

```html
<daisy-mockup-phone>
  <div class="text-white bg-neutral-900 grid place-content-center h-full">
    It's Glowtime.
  </div>
</daisy-mockup-phone>
```

## Inputs

- `borderColor`: `string | null` - The color of the phone's border.
- `customClass`: `string` - Custom classes to add to the mockup phone container.

## Content Projection

The content inside the `<daisy-mockup-phone>` tags will be displayed within the phone's screen area.

## Example

```typescript
import { Component } from '@angular/core';
import { MockupPhoneComponent } from './daisy-ui/mockup-phone/mockup-phone.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [MockupPhoneComponent],
  template: `
    <daisy-mockup-phone [borderColor]="'#ff8938'">
      <img alt="wallpaper" src="https://img.daisyui.com/images/stock/453966.webp" />
    </daisy-mockup-phone>
  `,
})
export class AppComponent {}
```
