
# Avatar Component

This component displays an avatar image or a placeholder.

## Usage

```html
<daisy-avatar [src]="'https://img.daisyui.com/images/profile/demo/batperson@192.webp'"></daisy-avatar>
```

## Inputs

- `src`: `string | null` - The image source for the avatar.
- `alt`: `string` - The alt text for the image.
- `size`: `'w-8' | 'w-12' | 'w-16' | 'w-20' | 'w-24' | 'w-32'` - The size of the avatar. Defaults to `w-24`.
- `shape`: `AvatarShape` - The shape of the avatar. Defaults to `rounded`.
- `mask`: `AvatarMask | null` - The mask to apply to the avatar.
- `online`: `boolean | null` - The presence indicator for the avatar.
- `placeholder`: `string` - The text to display if `src` is not provided.
- `customClass`: `string` - Custom classes to add to the component.

## Example

```typescript
import { Component } from '@angular/core';
import { AvatarComponent } from './daisy-ui/avatar/avatar.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [AvatarComponent],
  template: `
    <daisy-avatar 
      [src]="'https://img.daisyui.com/images/profile/demo/yellingcat@192.webp'"
      [shape]="'rounded-full'"
      [online]="true"
    ></daisy-avatar>
    <daisy-avatar
      [placeholder]="'AI'"
      [size]="'w-16'"
      [shape]="'rounded-full'"
    ></daisy-avatar>
  `,
})
export class AppComponent {}
```
