
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'daisy-mockup-phone',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="mockup-phone" [style.border-color]="borderColor" [class]="customClass">
      <div class="mockup-phone-camera"></div>
      <div class="mockup-phone-display">
        <ng-content></ng-content>
      </div>
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MockupPhoneComponent {
  @Input() borderColor: string | null = null;
  @Input() customClass = '';
}
