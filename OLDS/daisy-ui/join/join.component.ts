
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

export type JoinDirection = 'horizontal' | 'vertical';

@Component({
  selector: 'daisy-join',
  standalone: true,
  imports: [CommonModule],
  template: `
    <div [class]="classes">
      <ng-content></ng-content>
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class JoinComponent {
  @Input() direction: JoinDirection | null = null;
  @Input() customClass = '';

  get classes(): string {
    const baseClasses = 'join';
    const directionClass = this.direction ? `join-${this.direction}` : '';

    return [baseClasses, directionClass, this.customClass]
      .filter(Boolean)
      .join(' ');
  }
}

@Component({
  selector: '[daisyJoinItem]',
  standalone: true,
  imports: [CommonModule],
  template: ` <ng-content></ng-content> `,
  host: {
    class: 'join-item',
  },
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class JoinItemDirective {}
