/**
 * OpenTelemetry Tracer Configuration for StoryForge TypeScript Microservices.
 */

export interface Span {
  name: string;
  attributes: Record<string, any>;
  end: () => void;
}

export class StoryForgeTracer {
  private serviceName: string;

  constructor(serviceName: string = "storyforge-web") {
    this.serviceName = serviceName;
  }

  startSpan(name: string, attributes: Record<string, any> = {}): Span {
    const startTime = Date.now();
    return {
      name,
      attributes: { ...attributes, serviceName: this.serviceName, startTime },
      end: () => {
        const durationMs = Date.now() - startTime;
        console.log(`[TraceSpan] ${this.serviceName}::${name} finished in ${durationMs}ms`);
      },
    };
  }
}
