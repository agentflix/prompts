
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'daisy-mockup-window',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div class="mockup-window border border-base-300 w-full" [class]="customClass">
      <div class="grid place-content-center border-t border-base-300 h-80">
        <ng-content></ng-content>
      </div>
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MockupWindowComponent {
  @Input() customClass = '';
}
