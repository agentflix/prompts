
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export type DockSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

@Component({
  selector: 'daisy-dock',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div [class]="classes">
      <ng-content></ng-content>
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DockComponent {
  @Input() size: DockSize | null = null;
  @Input() customClass = '';

  get classes(): string {
    const baseClasses = 'dock relative border border-base-300';
    const sizeClass = this.size ? `dock-${this.size}` : '';

    return [baseClasses, sizeClass, this.customClass]
      .filter(Boolean)
      .join(' ');
  }
}

@Component({
  selector: 'button[daisy-dock-item]',
  standalone: true,
  imports: [CommonModule],
  template: `
    <ng-content></ng-content>
    @if (label) {
    <span class="dock-label">{{ label }}</span>
    }
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DockItemComponent {
  @Input() active = false;
  @Input() label: string | null = null;
  @Input() customClass = '';

  @Input()
  @HostBinding('class')
  get classes(): string {
    const activeClass = this.active ? 'dock-active' : '';
    return `${activeClass} ${this.customClass}`.trim();
  }
}
