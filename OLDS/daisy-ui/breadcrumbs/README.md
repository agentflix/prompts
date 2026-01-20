
# Breadcrumbs Component

This component displays a breadcrumb navigation.

## Usage

```html
<daisy-breadcrumbs [items]="breadcrumbItems"></daisy-breadcrumbs>
```

## Inputs

- `items`: `BreadcrumbItem[]` - An array of items to display in the breadcrumbs.

## Interface

```typescript
export interface BreadcrumbItem {
  label: string;
  link?: string;
}
```

## Example

```typescript
import { Component } from '@angular/core';
import { BreadcrumbsComponent, BreadcrumbItem } from './daisy-ui/breadcrumbs/breadcrumbs.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [BreadcrumbsComponent],
  template: `
    <daisy-breadcrumbs [items]="breadcrumbItems"></daisy-breadcrumbs>
  `,
})
export class AppComponent {
  breadcrumbItems: BreadcrumbItem[] = [
    {
      label: 'Home',
      link: '/',
    },
    {
      label: 'Documents',
      link: '/documents',
    },
    {
      label: 'Add Document',
    },
  ];
}
```
