
# Countdown Component

This component displays a number with a transition effect, typically used for countdowns.

## Usage

```html
<daisy-countdown [value]="59"></daisy-countdown>
```

## Inputs

- `value`: `number` - The number to display. Must be between 0 and 999.
- `digits`: `1 | 2 | 3 | null` - The minimum number of digits to display. Can be `1`, `2`, or `3`.
- `customClass`: `string` - Custom classes to add to the component.

## Example

```typescript
import { Component, OnInit, OnDestroy } from '@angular/core';
import { CommonModule } from '@angular/common';
import { CountdownComponent } from './daisy-ui/countdown/countdown.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, CountdownComponent],
  template: `
    <div class="flex gap-5">
      <div>
        <span class="font-mono text-4xl countdown">
          <daisy-countdown [value]="days"></daisy-countdown>
        </span>
        days
      </div>
      <div>
        <span class="font-mono text-4xl countdown">
          <daisy-countdown [value]="hours"></daisy-countdown>
        </span>
        hours
      </div>
      <div>
        <span class="font-mono text-4xl countdown">
          <daisy-countdown [value]="minutes"></daisy-countdown>
        </span>
        min
      </div>
      <div>
        <span class="font-mono text-4xl countdown">
          <daisy-countdown [value]="seconds"></daisy-countdown>
        </span>
        sec
      </div>
    </div>
  `,
})
export class AppComponent implements OnInit, OnDestroy {
  days = 15;
  hours = 10;
  minutes = 24;
  seconds = 59;
  private intervalId: any;

  ngOnInit() {
    this.intervalId = setInterval(() => {
      this.seconds--;
      if (this.seconds < 0) {
        this.seconds = 59;
        this.minutes--;
        if (this.minutes < 0) {
          this.minutes = 59;
          this.hours--;
          if (this.hours < 0) {
            this.hours = 23;
            this.days--;
            if (this.days < 0) {
              this.days = 0; // Stop countdown or reset
              clearInterval(this.intervalId);
            }
          }
        }
      }
    }, 1000);
  }

  ngOnDestroy() {
    if (this.intervalId) {
      clearInterval(this.intervalId);
    }
  }
}
```
