
import {
  ChangeDetectionStrategy,
  Component,
  CUSTOM_ELEMENTS_SCHEMA,
  ElementRef,
  EventEmitter,
  Input,
  OnInit,
  Output,
  ViewChild,
} from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'daisy-calendar',
  standalone: true,
  imports: [CommonModule],
  template: `
    <calendar-date
      #cally
      class="cally bg-base-100 border border-base-300 shadow-lg rounded-box"
      (change)="onDateChange($event)">
      <svg
        aria-label="Previous"
        class="fill-current size-4"
        slot="previous"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24">
        <path
          fill="currentColor"
          d="M15.75 19.5 8.25 12l7.5-7.5"></path>
      </svg>
      <svg
        aria-label="Next"
        class="fill-current size-4"
        slot="next"
        xmlns="http://www.w3.org/2000/svg"
        viewBox="0 0 24 24">
        <path
          fill="currentColor"
          d="m8.25 4.5 7.5 7.5-7.5 7.5"></path>
      </svg>
      <calendar-month></calendar-month>
    </calendar-date>
  `,
  schemas: [CUSTOM_ELEMENTS_SCHEMA],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CalendarComponent implements OnInit {
  @ViewChild('cally', { static: true }) cally!: ElementRef<HTMLElement>;
  @Output() dateChange = new EventEmitter<string>();

  ngOnInit() {
    // It is necessary to load the cally script dynamically
    // because it is a web component and it is not available
    // in the global scope when the component is initialized.
    const script = document.createElement('script');
    script.type = 'module';
    script.src = 'https://unpkg.com/cally';
    document.head.appendChild(script);
  }

  onDateChange(event: Event) {
    const value = (event.target as HTMLInputElement).value;
    this.dateChange.emit(value);
  }
}
