from properties.models import ExchangeOffer


def score(a: ExchangeOffer, b: ExchangeOffer) -> int:
    sc = 0
    if a.want_city and b.my_city and a.want_city.lower() == b.my_city.lower():
        sc += 2
    if (
        a.want_property_type
        and b.my_property_type
        and a.want_property_type == b.my_property_type
    ):
        sc += 2
    if a.want_min_rooms and b.my_rooms >= a.want_min_rooms:
        sc += 1
    if a.want_min_area and b.my_living_area >= a.want_min_area:
        sc += 1
    if a.want_garden and b.my_garden:
        sc += 1
    if a.want_balcony and b.my_balcony:
        sc += 1
    if a.want_terrace and b.my_terrace:
        sc += 1
    if a.want_storage and b.my_storage:
        sc += 1
    if a.want_attic and b.my_attic:
        sc += 1
    if a.want_cellar and b.my_cellar:
        sc += 1
    if a.want_parking_private and b.my_parking_private:
        sc += 1
    if a.want_ov and b.my_ov:
        sc += 1
    return sc


def find_matches_for(offer: ExchangeOffer):
    if not offer:
        return []
    qs = ExchangeOffer.objects.filter(is_published=True).exclude(pk=offer.pk)
    results = []
    for cand in qs:
        total = score(offer, cand) + score(cand, offer)
        if total >= 3:
            results.append((cand, total))
    results.sort(key=lambda t: -t[1])
    return results[:20]
