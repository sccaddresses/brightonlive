# Privacy and address safety

BrightonLive must distinguish:
- a public customer-facing/trading address;
- a registered office;
- a charity contact address;
- a home/service-provider administrative address;
- a service area with no public destination.

`address_public`, `phone_public` and `email_public` are explicit.

The public exporter strips suppressed contact/address data and removes map geometry when the
address is not public.

Companies House is used for corporate identity/corroboration, never as sole proof of a public
Brighton trading location.
