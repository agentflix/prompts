
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export type MenuDirection = 'vertical' | 'horizontal';
export type MenuSize = 'xs' | 'sm' | 'md' | 'lg' | 'xl';

@Component({
  selector: 'daisy-menu',
  standalone: true,
  imports: [CommonModule],
  template: `
    <ul [class]="classes">
      <ng-content></ng-content>
    </ul>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MenuComponent {
  @Input() direction: MenuDirection = 'vertical';
  @Input() size: MenuSize | null = null;
  @Input() customClass = '';

  get classes(): string {
    const baseClasses = 'menu';
    const directionClass = `menu-${this.direction}`;
    const sizeClass = this.size ? `menu-${this.size}` : '';

    return [baseClasses, directionClass, sizeClass, this.customClass]
      .filter(Boolean)
      .join(' ');
  }
}

@Component({
  selector: 'li[daisy-menu-item]',
  standalone: true,
  imports: [CommonModule],
  template: `
    <ng-container *ngIf="!isDropdown; else dropdownContent">
      <a [class]="itemClasses">
        <ng-content></ng-content>
      </a>
    </ng-container>
    <ng-template #dropdownContent>
      <details [open]="dropdownOpen">
        <summary [class]="itemClasses">
          <ng-content select="[menu-summary]"></ng-content>
        </summary>
        <ul>
          <ng-content select="[menu-dropdown-content]"></ng-content>
        </ul>
      </details>
    </ng-template>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MenuItemComponent {
  @Input() active = false;
  @Input() disabled = false;
  @Input() isDropdown = false;
  @Input() dropdownOpen = false;
  @Input() customClass = '';

  get itemClasses(): string {
    const activeClass = this.active ? 'menu-active' : '';
    const disabledClass = this.disabled ? 'menu-disabled' : '';
    return [activeClass, disabledClass, this.customClass].filter(Boolean).join(' ');
  }
}

@Component({
  selector: 'li[daisy-menu-title]',
  standalone: true,
  imports: [CommonModule],
  template: `
    <h2 class="menu-title">
      <ng-content></ng-content>
    </h2>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MenuTitleComponent {}
