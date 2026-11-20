/**
 * Core engine for Capital Train (LRT) calculations
 */
export interface Station {
  id: string;
  name_ar: string;
  name_en: string;
  branch: 'main' | 'junction' | 'capital' | 'ramadan';
  is_interchange: boolean;
  connections: string[];
  travel_time_from_prev: number;
}

export interface RouteResult {
  from: Station;
  to: Station;
  stationsCount: number;
  estimatedMinutes: number;
  ticketPriceEgp: number;
  monthlyPassEgp: number;
  transferRequired: boolean;
  transferStation?: string;
  stationsList: Station[];
  nextDepartures: string[];
}

export class LRTEngine {
  private data: any;

  constructor(jsonData: any) {
    this.data = jsonData;
  }

  getStations(): Station[] {
    return this.data.stations;
  }

  getStationById(id: string): Station | undefined {
    return this.data.stations.find((s: Station) => s.id === id);
  }

  calculateFare(numStations: number): { ticket: number; monthly: number } {
    for (const rule of this.data.fare_rules) {
      if (numStations <= rule.max_stations) {
        return { ticket: rule.ticket_price_egp, monthly: rule.monthly_pass_egp };
      }
    }
    return { ticket: 20, monthly: 600 };
  }

  // Calculate route between origin and destination
  planTrip(fromId: string, toId: string): RouteResult | null {
    const from = this.getStationById(fromId);
    const to = this.getStationById(toId);
    if (!from || !to || from.id === to.id) return null;

    const stations = this.data.stations;
    const mainStations = stations.filter((s: Station) => s.branch === 'main' || s.branch === 'junction');
    const capitalStations = stations.filter((s: Station) => s.branch === 'capital');
    const ramadanStations = stations.filter((s: Station) => s.branch === 'ramadan');

    const badr = stations.find((s: Station) => s.id === 'badr');

    let path: Station[] = [];
    let transferRequired = false;

    // Check branch switching (e.g. from capital to ramadan or vice versa)
    if ((from.branch === 'capital' && to.branch === 'ramadan') || (from.branch === 'ramadan' && to.branch === 'capital')) {
      transferRequired = true;
      const part1 = this.findLinearPath(from, badr!);
      const part2 = this.findLinearPath(badr!, to);
      path = [...part1, ...part2.slice(1)];
    } else {
      path = this.findLinearPath(from, to);
    }

    const stationsCount = path.length - 1;
    let estimatedMinutes = 0;
    for (let i = 1; i < path.length; i++) {
      estimatedMinutes += path[i].travel_time_from_prev || 5;
    }
    if (transferRequired) {
      estimatedMinutes += 6; // Transfer waiting buffer
    }

    const fare = this.calculateFare(stationsCount);
    const nextDepartures = this.getNextDepartures(new Date());

    return {
      from,
      to,
      stationsCount,
      estimatedMinutes,
      ticketPriceEgp: fare.ticket,
      monthlyPassEgp: fare.monthly,
      transferRequired,
      transferStation: transferRequired ? 'محطة بدر' : undefined,
      stationsList: path,
      nextDepartures
    };
  }

  private findLinearPath(from: Station, to: Station): Station[] {
    const stations: Station[] = this.data.stations;
    // Build tree/order based on branches
    const getOrderIndex = (st: Station) => {
      if (st.branch === 'main') {
        const order = ['adly_mansour', 'el_obour', 'el_mostakbal', 'el_shorouk', 'new_heliopolis'];
        return order.indexOf(st.id);
      }
      if (st.id === 'badr') return 5;
      if (st.branch === 'capital') {
        const order = ['el_robaikey', 'capital_gardens', 'capital_airport', 'arts_and_culture'];
        return 6 + order.indexOf(st.id);
      }
      if (st.branch === 'ramadan') {
        const order = ['industrial_zone', 'knowledge_city'];
        return 10 + order.indexOf(st.id);
      }
      return 0;
    };

    // Return sequenced path
    const branch1 = ['adly_mansour', 'el_obour', 'el_mostakbal', 'el_shorouk', 'new_heliopolis', 'badr', 'el_robaikey', 'capital_gardens', 'capital_airport', 'arts_and_culture'];
    const branch2 = ['adly_mansour', 'el_obour', 'el_mostakbal', 'el_shorouk', 'new_heliopolis', 'badr', 'industrial_zone', 'knowledge_city'];

    let seq = branch1;
    if (from.branch === 'ramadan' || to.branch === 'ramadan') {
      seq = branch2;
    }

    const idx1 = seq.indexOf(from.id);
    const idx2 = seq.indexOf(to.id);
    if (idx1 === -1 || idx2 === -1) return [from, to];

    const resultIds = idx1 <= idx2 ? seq.slice(idx1, idx2 + 1) : seq.slice(idx2, idx1 + 1).reverse();
    return resultIds.map(id => this.getStationById(id)!);
  }

  getCurrentHeadwayMinutes(timeStr: string): { headway: number; isPeak: boolean } {
    for (const rule of this.data.headway_schedule) {
      if (timeStr >= rule.start_time && timeStr < rule.end_time) {
        return { headway: rule.headway_minutes, isPeak: !!rule.is_peak };
      }
    }
    return { headway: 15, isPeak: false };
  }

  getNextDepartures(currentTime: Date, count: number = 3): string[] {
    const hours = currentTime.getHours();
    const minutes = currentTime.getMinutes();
    const currentMinsTotal = hours * 60 + minutes;

    const firstMins = 6 * 60; // 06:00
    const lastMins = 23 * 60 + 20; // 23:20

    if (currentMinsTotal < firstMins) {
      return ['06:00', '06:15', '06:30'];
    }
    if (currentMinsTotal > lastMins) {
      return ['الخدمة متوقفة الآن - أول قطار غداً 06:00 ص'];
    }

    const departures: string[] = [];
    let t = firstMins;
    while (t <= lastMins) {
      const hStr = Math.floor(t / 60).toString().padStart(2, '0');
      const mStr = (t % 60).toString().padStart(2, '0');
      const timeStr = `${hStr}:${mStr}`;
      const { headway } = this.getCurrentHeadwayMinutes(timeStr);

      if (t >= currentMinsTotal) {
        departures.push(timeStr);
        if (departures.length >= count) break;
      }
      t += headway;
    }
    return departures;
  }
}
