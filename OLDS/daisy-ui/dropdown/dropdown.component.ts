
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export type DropdownPlacement =
  | 'start'
  | 'center'
  | 'end'
  | 'top'
  | 'bottom'
  | 'left'
  | 'right';

@Component({
  selector: 'daisy-dropdown',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div [class]="classes">
      <div tabindex="0" role="button" [class]="triggerClasses">
        <ng-content select="[dropdown-trigger]"></ng-content>
      </div>
      <div tabindex="-1" [class]="contentClasses">
        <ng-content select="[dropdown-content]"></ng-content>
      </div>
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DropdownComponent {
  @Input() placement: DropdownPlacement[] = [];
  @Input() hover = false;
  @Input() open = false;
  @Input() customClass = '';
  @Input() contentCustomClass = '';
  @Input() triggerCustomClass = '';

  get classes(): string {
    const baseClasses = 'dropdown';
    const placementClasses = this.placement
      .map((p) => `dropdown-${p}`)
      .join(' ');
    const hoverClass = this.hover ? 'dropdown-hover' : '';
    const openClass = this.open ? 'dropdown-open' : '';

    return [baseClasses, placementClasses, hoverClass, openClass, this.customClass]
      .filter(Boolean)
      .join(' ');
  }

  get triggerClasses(): string {
    return `m-1 btn ${this.triggerCustomClass}`.trim();
  }

  get contentClasses(): string {
    return `p-2 shadow-sm menu dropdown-content z-1 bg-base-100 rounded-box w-52 ${this.contentCustomClass}`.trim();
  }
}
