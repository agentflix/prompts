
import { ChangeDetectionStrategy, Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { AvatarComponent } from '../avatar/avatar.component';

export type ChatPlacement = 'start' | 'end';
export type ChatBubbleColor =
  | 'primary'
  | 'secondary'
  | 'accent'
  | 'neutral'
  | 'info'
  | 'success'
  | 'warning'
  | 'error';

@Component({
  selector: 'daisy-chat',
  standalone: true,
  imports: [CommonModule, AvatarComponent],
  template: `
    <div [class]="chatClasses">
      @if (avatarSrc) {
      <div class="chat-image">
        <daisy-avatar [src]="avatarSrc" [alt]="avatarAlt" size="w-10" shape="rounded-full"></daisy-avatar>
      </div>
      }
      @if (header) {
      <div class="chat-header">
        {{ header }}
        @if (time) {
        <time class="text-xs opacity-50">{{ time }}</time>
        }
      </div>
      }
      <div [class]="bubbleClasses">
        <ng-content></ng-content>
      </div>
      @if (footer) {
      <div class="chat-footer opacity-50">
        {{ footer }}
      </div>
      }
    </div>
  `,
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class ChatComponent {
  @Input() placement: ChatPlacement = 'start';
  @Input() color: ChatBubbleColor | null = null;
  @Input() avatarSrc: string | null = null;
  @Input() avatarAlt = '';
  @Input() header: string | null = null;
  @Input() time: string | null = null;
  @Input() footer: string | null = null;
  @Input() customClass = '';

  get chatClasses(): string {
    return `chat chat-${this.placement} ${this.customClass}`.trim();
  }

  get bubbleClasses(): string {
    const colorClass = this.color ? `chat-bubble-${this.color}` : '';
    return `chat-bubble ${colorClass}`.trim();
  }
}
