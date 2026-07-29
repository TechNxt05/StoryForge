/**
 * Prometheus Metrics Exporter Definitions for StoryForge.
 */

export class PrometheusMetricsExporter {
  private counters: Map<string, number> = new Map();

  incrementCounter(name: string, value: number = 1): number {
    const current = this.counters.get(name) || 0;
    const updated = current + value;
    this.counters.set(name, updated);
    return updated;
  }

  getMetricsString(): string {
    let output = "# HELP storyforge_metrics System performance metrics\n";
    this.counters.forEach((val, key) => {
      output += `storyforge_${key} ${val}\n`;
    });
    return output;
  }
}
