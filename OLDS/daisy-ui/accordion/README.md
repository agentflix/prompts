
# Accordion Component

This component creates an accordion from a list of items.

## Usage

```html
<daisy-accordion [items]="accordionItems"></daisy-accordion>
```

## Inputs

- `items`: `AccordionItem[]` - An array of items to display in the accordion.
- `name`: `string` - The name of the accordion group. Defaults to `accordion`.
- `customClass`: `string` - Custom classes to add to the component.

## Interface

```typescript
export interface AccordionItem {
  title: string;
  content: string;
  checked?: boolean;
}
```

## Example

```typescript
import { Component } from '@angular/core';
import { AccordionComponent, AccordionItem } from './daisy-ui/accordion/accordion.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [AccordionComponent],
  template: `
    <daisy-accordion [items]="accordionItems"></daisy-accordion>
  `,
})
export class AppComponent {
  accordionItems: AccordionItem[] = [
    {
      title: 'How do I create an account?',
      content: 'Click the "Sign Up" button in the top right corner and follow the registration process.',
      checked: true,
    },
    {
      title: 'I forgot my password. What should I do?',
      content: 'Click on "Forgot Password" on the login page and follow the instructions sent to your email.',
    },
    {
      title: 'How do I update my profile information?',
      content: 'Go to "My Account" settings and select "Edit Profile" to make changes.',
    },
  ];
}
```
