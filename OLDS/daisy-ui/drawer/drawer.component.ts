
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

export type DrawerSide = 'start' | 'end';

@Component({
  selector: 'daisy-drawer',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="drawer" [class]="sideClass">
      <input [id]="id" type="checkbox" class="drawer-toggle" [(ngModel)]="isOpen" />
      <div class="drawer-content">
        <ng-content select="[drawer-content]"></ng-content>
      </div>
      <div class="drawer-side">
        <label [for]="id" aria-label="close sidebar" class="drawer-overlay"></label>
        <ng-content select="[drawer-side]"></ng-content>
      </div>
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class DrawerComponent {
  @Input() id!: string;
  @Input() isOpen = false;
  @Input() side: DrawerSide = 'start';
  @Input() customClass = '';

  get sideClass(): string {
    return this.side === 'end' ? 'drawer-end' : '';
  }
}
