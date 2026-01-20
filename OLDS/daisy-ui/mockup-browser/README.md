
# Browser Mockup Component

This component displays a box that looks like a browser window, useful for showcasing web content.

## Usage

```html
<daisy-mockup-browser [url]="'https://example.com'">
  <p>Your website content goes here!</p>
</daisy-mockup-browser>
```

## Inputs

- `url`: `string` - The URL to display in the browser's address bar. Defaults to `https://daisyui.com`.
- `customClass`: `string` - Custom classes to add to the mockup browser container.

## Content Projection

The content inside the `<daisy-mockup-browser>` tags will be displayed within the browser window's content area.

## Example

```typescript
import { Component } from '@angular/core';
import { MockupBrowserComponent } from './daisy-ui/mockup-browser/mockup-browser.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [MockupBrowserComponent],
  template: `
    <daisy-mockup-browser [url]="'https://agentflix.com'" customClass="bg-base-100">
      <div class="p-4">
        <h2 class="text-xl font-bold">Welcome to AgentFlix!</h2>
        <p>This is a demo of our awesome platform.</p>
      </div>
    </daisy-mockup-browser>
  `,
})
export class AppComponent {}
```
