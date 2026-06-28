from pydantic import BaseModel, Field, ConfigDict


class SpringBookingRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    name: str = ""
    email: str = ""
    trip_category: str | None = Field(default=None, alias="tripCategory")
    trip_type: str | None = Field(default=None, alias="tripType")
    from_location: str = Field(alias="fromLocation")
    to_location: str = Field(alias="toLocation")
    city: str | None = None
    pickup_location: str | None = Field(default=None, alias="pickupLocation")
    pickup_date: str = Field(alias="pickupDate")
    pickup_time: str = Field(default="00:00", alias="pickupTime")
    mobile: str | None = None
    vehicle_name: str | None = Field(default=None, alias="vehicleName")
    distance_km: float = Field(default=0.0, alias="distanceKm")
    fare: float = 0.0


class SpringBookingResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    booking_id: int = Field(alias="bookingId")
    status: str
    vehicle_name: str | None = Field(default=None, alias="vehicleName")
    from_location: str | None = Field(default=None, alias="fromLocation")
    to_location: str | None = Field(default=None, alias="toLocation")
    trip_type: str | None = Field(default=None, alias="tripType")
    distance_km: float = Field(default=0.0, alias="distanceKm")
    fare: float = 0.0
    pickup_date: str | None = Field(default=None, alias="pickupDate")
    pickup_time: str | None = Field(default=None, alias="pickupTime")
    mobile_no: str | None = Field(default=None, alias="mobileNo")


class SpringBookingStatusResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    booking_id: int = Field(alias="bookingId")
    status: str
    vehicle_name: str | None = Field(default=None, alias="vehicleName")
    from_location: str | None = Field(default=None, alias="fromLocation")
    to_location: str | None = Field(default=None, alias="toLocation")
    fare: float = 0.0
    pickup_date: str | None = Field(default=None, alias="pickupDate")