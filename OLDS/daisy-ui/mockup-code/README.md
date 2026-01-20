
# Code Mockup Component

This component displays a block of code in a box that looks like a code editor.

## Usage

```html
<daisy-mockup-code [codeLines]="myCode"></daisy-mockup-code>
```

## Inputs

- `codeLines`: `CodeLine[]` - An array of objects, each representing a line of code.
- `customClass`: `string` - Custom classes to add to the mockup code container.

## Interface

```typescript
export interface CodeLine {
  code: string;
  prefix?: string;
  class?: string;
}
```

## Example

```typescript
import { Component } from '@angular/core';
import { MockupCodeComponent, CodeLine } from './daisy-ui/mockup-code/mockup-code.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [MockupCodeComponent],
  template: `
    <daisy-mockup-code [codeLines]="exampleCode" customClass="w-full">
    </daisy-mockup-code>
  `,
})
export class AppComponent {
  exampleCode: CodeLine[] = [
    { prefix: '$', code: 'npm i daisyui' },
    { prefix: '>', code: 'installing...', class: 'text-warning' },
    { prefix: '>', code: 'Done!', class: 'text-success' },
    {
      prefix: '~',
      code: 'Magnam dolore beatae necessitatibus nemopsum itaque sit. Et porro quae qui et et dolore ratione.',
    },
    { code: 'without prefix' },
  ];
}
```
