
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'daisy-mockup-browser',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="mockup-browser border border-base-300 w-full" [class]="customClass">
      <div class="mockup-browser-toolbar">
        <div class="input">{{ url }}</div>
      </div>
      <div class="grid place-content-center border-t border-base-300 h-80">
        <ng-content></ng-content>
      </div>
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MockupBrowserComponent {
  @Input() url = 'https://daisyui.com';
  @Input() customClass = '';
}
