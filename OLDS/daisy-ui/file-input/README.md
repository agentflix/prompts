
# File Input Component

This component provides a styled file input field.

## Usage

```html
<daisy-file-input (fileChange)="onFileSelected($event)"></daisy-file-input>
```

## Inputs

- `color`: `FileInputColor | null` - The color of the file input.
- `size`: `FileInputSize | null` - The size of the file input.
- `ghost`: `boolean` - If true, applies the ghost style.
- `disabled`: `boolean` - Whether the file input is disabled.
- `placeholder`: `string` - The placeholder text for the file input.
- `customClass`: `string` - Custom classes to add to the component.

## Outputs

- `fileChange`: `EventEmitter<FileList | null>` - Emits the selected `FileList` when files are chosen.

## Example

```typescript
import { Component } from '@angular/core';
import { FileInputComponent } from './daisy-ui/file-input/file-input.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [FileInputComponent],
  template: `
    <daisy-file-input
      [color]="'primary'"
      [size]="'lg'"
      [placeholder]="'Choose your file'"
      (fileChange)="onFileSelected($event)"
    ></daisy-file-input>
  `,
})
export class AppComponent {
  onFileSelected(files: FileList | null) {
    if (files && files.length > 0) {
      console.log('Selected file:', files[0].name);
    }
  }
}
```
