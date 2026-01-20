
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

export type CollapseIcon = 'arrow' | 'plus';

@Component({
  selector: 'daisy-collapse',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div [class]="classes" [attr.tabindex]="!checkbox ? 0 : null">
      @if (checkbox) {
      <input type="checkbox" [checked]="open" (change)="onToggle()" />
      }
      <div class="collapse-title font-semibold">
        <ng-content select="[collapse-title]"></ng-content>
      </div>
      <div class="collapse-content text-sm">
        <ng-content select="[collapse-content]"></ng-content>
      </div>
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class CollapseComponent {
  @Input() icon: CollapseIcon | null = null;
  @Input() open = false;
  @Input() checkbox = false;
  @Input() customClass = '';

  get classes(): string {
    const baseClasses = 'collapse bg-base-100 border border-base-300';
    const iconClass = this.icon ? `collapse-${this.icon}` : '';
    const openClass = this.open && !this.checkbox ? 'collapse-open' : '';
    const closeClass = !this.open && !this.checkbox ? 'collapse-close' : '';

    return [
      baseClasses,
      iconClass,
      openClass,
      closeClass,
      this.customClass,
    ]
      .filter(Boolean)
      .join(' ');
  }

  onToggle(): void {
    this.open = !this.open;
  }
}
