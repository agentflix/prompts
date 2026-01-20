
# Calendar Component

This component is a wrapper around the [Cally web component](https://github.com/WickyNilliams/cally).

## Usage

```html
<daisy-calendar (dateChange)="onDateChange($event)"></daisy-calendar>
```

## Outputs

- `dateChange`: `EventEmitter<string>` - Emits the selected date as a string.

## Example

```typescript
import { Component } from '@angular/core';
import { CalendarComponent } from './daisy-ui/calendar/calendar.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CalendarComponent],
  template: `
    <daisy-calendar (dateChange)="onDateChange($event)"></daisy-calendar>
  `,
})
export class AppComponent {
  onDateChange(date: string) {
    console.log(date);
  }
}
```

## Important

This component uses a web component library called `cally`. The component automatically loads the library from a CDN.
You also need to add `CUSTOM_ELEMENTS_SCHEMA` to your module or component schemas to allow the use of custom elements.

```typescript
import { CUSTOM_ELEMENTS_SCHEMA, NgModule } from '@angular/core';

@NgModule({
  // ...
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
})
export class AppModule {}
```
