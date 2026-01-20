
# Chat Component

This component displays a chat bubble.

## Usage

```html
<daisy-chat [placement]="'start'" [header]="'Obi-Wan Kenobi'" [time]="'12:45'" [avatarSrc]="'https://img.daisyui.com/images/profile/demo/kenobee@192.webp'">
  You were the Chosen One!
</daisy-chat>
```

## Inputs

- `placement`: `ChatPlacement` - Aligns the chat bubble. Can be `start` or `end`. Defaults to `start`.
- `color`: `ChatBubbleColor | null` - The color of the chat bubble.
- `avatarSrc`: `string | null` - The source URL for the avatar image.
- `avatarAlt`: `string` - The alt text for the avatar image.
- `header`: `string | null` - Text displayed above the chat bubble (e.g., sender's name).
- `time`: `string | null` - Time displayed next to the header.
- `footer`: `string | null` - Text displayed below the chat bubble (e.g., delivery status).
- `customClass`: `string` - Custom classes to add to the chat container.

## Content Projection

The main content of the chat bubble is projected into the component using `<ng-content>`.

## Example

```typescript
import { Component } from '@angular/core';
import { ChatComponent } from './daisy-ui/chat/chat.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [ChatComponent],
  template: `
    <daisy-chat
      [placement]="'start'"
      [avatarSrc]="'https://img.daisyui.com/images/profile/demo/kenobee@192.webp'"
      [header]="'Obi-Wan Kenobi'"
      [time]="'12:45'"
      [footer]="'Delivered'"
      [color]="'primary'"
    >
      It's over Anakin, I have the high ground.
    </daisy-chat>
    <daisy-chat
      [placement]="'end'"
      [avatarSrc]="'https://img.daisyui.com/images/profile/demo/anakeen@192.webp'"
      [header]="'Anakin'"
      [time]="'12:46'"
      [footer]="'Seen at 12:46'"
      [color]="'error'"
    >
      You underestimate my power!
    </daisy-chat>
  `,
})
export class AppComponent {}
```
