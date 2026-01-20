
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'daisy-fab',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div [class]="classes">
      <ng-content></ng-content>
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class FabComponent {
  @Input() flower = false;
  @Input() customClass = '';

  get classes(): string {
    const baseClasses = 'fab absolute z-1';
    const flowerClass = this.flower ? 'fab-flower' : '';

    return [baseClasses, flowerClass, this.customClass]
      .filter(Boolean)
      .join(' ');
  }
}
