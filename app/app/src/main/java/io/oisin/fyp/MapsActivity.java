package io.oisin.fyp;

import android.Manifest;
import android.content.Context;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.location.Criteria;
import android.location.Location;
import android.location.LocationManager;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.TextView;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.toolbox.StringRequest;
import com.android.volley.toolbox.Volley;
import com.github.mikephil.charting.charts.LineChart;
import com.github.mikephil.charting.components.XAxis;
import com.github.mikephil.charting.components.YAxis;
import com.github.mikephil.charting.data.Entry;
import com.github.mikephil.charting.data.LineData;
import com.github.mikephil.charting.data.LineDataSet;
import com.github.mikephil.charting.formatter.ValueFormatter;
import com.github.mikephil.charting.utils.ColorTemplate;
import com.google.android.gms.common.api.Status;
import com.google.android.gms.maps.CameraUpdate;
import com.google.android.gms.maps.CameraUpdateFactory;
import com.google.android.gms.maps.GoogleMap;
import com.google.android.gms.maps.OnMapReadyCallback;
import com.google.android.gms.maps.OnStreetViewPanoramaReadyCallback;
import com.google.android.gms.maps.StreetViewPanorama;
import com.google.android.gms.maps.SupportMapFragment;
import com.google.android.gms.maps.SupportStreetViewPanoramaFragment;
import com.google.android.gms.maps.model.BitmapDescriptorFactory;
import com.google.android.gms.maps.model.Dot;
import com.google.android.gms.maps.model.Gap;
import com.google.android.gms.maps.model.JointType;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.LatLngBounds;
import com.google.android.gms.maps.model.MapStyleOptions;
import com.google.android.gms.maps.model.Marker;
import com.google.android.gms.maps.model.MarkerOptions;
import com.google.android.gms.maps.model.PatternItem;
import com.google.android.gms.maps.model.Polyline;
import com.google.android.gms.maps.model.PolylineOptions;
import com.google.android.gms.maps.model.RoundCap;
import com.google.android.libraries.places.api.Places;
import com.google.android.libraries.places.api.model.Place;
import com.google.android.libraries.places.api.model.RectangularBounds;
import com.google.android.libraries.places.widget.AutocompleteSupportFragment;
import com.google.android.libraries.places.widget.listener.PlaceSelectionListener;
import com.google.android.material.bottomsheet.BottomSheetBehavior;
import com.google.maps.android.clustering.ClusterItem;
import com.google.maps.android.clustering.ClusterManager;
import com.google.maps.android.clustering.view.DefaultClusterRenderer;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.nio.charset.Charset;
import java.text.DateFormat;
import java.text.SimpleDateFormat;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.Date;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Objects;
import java.util.concurrent.TimeUnit;

import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;
import androidx.fragment.app.FragmentActivity;

/**
 * This version of the map has clustering
 */
public class MapsActivity extends FragmentActivity implements OnMapReadyCallback, ActivityCompat.OnRequestPermissionsResultCallback, GoogleMap.OnMarkerClickListener {

    private GoogleMap mMap;
    private StreetViewPanorama mStreetViewPanorama;
    private ClusterManager<StationClusterItem> mClusterManager;
    private static final int PERMISSIONS_REQUEST_ACCESS_FINE_LOCATION = 1;
    private RequestQueue queue;
    private Map<String, StationClusterItem> clusterItems = new HashMap<>();
    private List<Polyline> routeLines = new ArrayList<>();

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_maps);

        SupportMapFragment mapFragment = (SupportMapFragment) getSupportFragmentManager()
                .findFragmentById(R.id.map);
        mapFragment.getMapAsync(this);

        queue = Volley.newRequestQueue(this);

        setUpMapUI();
        setUpGraph();
        setUpAutocomplete();
        setUpBottomSheet();

        pingRoutingServer();
    }

    private void pingRoutingServer() {
        String url ="https://oisin-flask-test.herokuapp.com/";

        // Request a string response from the provided URL.
        StringRequest stringRequest = new StringRequest(Request.Method.GET, url,
                new Response.Listener<String>() {
                    @Override
                    public void onResponse(String response) {
                        // Display the first 500 characters of the response string.
                        Log.d("RouteActivity", "ping:  " + response);
                    }
                }, new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError error) {
                Log.e("RouteActivity", "error with ping");
            }
        });

        queue.add(stringRequest);
    }

    private void setUpGraph() {
        LineChart chart = findViewById(R.id.availability_chart);
        chart.setBackgroundColor(Color.WHITE);

        XAxis xAxis = chart.getXAxis();
        xAxis.setPosition(XAxis.XAxisPosition.TOP_INSIDE);
        xAxis.setTextSize(10f);
        xAxis.setTextColor(Color.WHITE);
        xAxis.setDrawAxisLine(false);
        xAxis.setDrawGridLines(true);
        xAxis.setTextColor(Color.rgb(255, 192, 56));
        xAxis.setCenterAxisLabels(true);
        xAxis.setGranularity(1f); // one hour
        xAxis.setValueFormatter(new ValueFormatter() {

            private final SimpleDateFormat mFormat = new SimpleDateFormat("HH:mm", Locale.ENGLISH);

            @Override
            public String getFormattedValue(float value) {

                long millis = TimeUnit.HOURS.toMillis((long) value);
                return mFormat.format(new Date((long) value));
            }
        });

        YAxis leftAxis = chart.getAxisLeft();
        leftAxis.setPosition(YAxis.YAxisLabelPosition.INSIDE_CHART);
        leftAxis.setTextColor(ColorTemplate.getHoloBlue());
        leftAxis.setDrawGridLines(true);
        leftAxis.setGranularityEnabled(true);
        leftAxis.setYOffset(-9f);
        leftAxis.setTextColor(Color.rgb(255, 192, 56));

        YAxis rightAxis = chart.getAxisRight();
        rightAxis.setEnabled(false);

        ArrayList<Entry> values = new ArrayList<>();

        InputStream is = getResources().openRawResource(R.raw.bikes);
        BufferedReader reader = new BufferedReader(
                new InputStreamReader(is, Charset.forName("UTF-8")));
        String line = "";

        try {
            reader.readLine();
            while ((line = reader.readLine()) != null) {
                // Split the line into different tokens (using the comma as a separator).
                String[] tokens = line.split(",");

//                // Read the data and store it in the WellData POJO.
                DateFormat dateFormat = new SimpleDateFormat("yyyy-MM-dd'T'HH:mm:ss", Locale.ENGLISH);
                values.add(new Entry((float) dateFormat.parse(tokens[4]).getTime(), Float.parseFloat(tokens[0])));

                //             values.add(new Entry(Float.parseFloat(tokens[1]), Float.parseFloat(tokens[0])));
            }
        } catch (Exception e1) {
            Log.e("MainActivity", "Error" + line, e1);
            e1.printStackTrace();
        }

        LineDataSet set1 = new LineDataSet(values, "Label");
        set1.setAxisDependency(YAxis.AxisDependency.LEFT);
        set1.setColor(ColorTemplate.getHoloBlue());
        set1.setValueTextColor(ColorTemplate.getHoloBlue());
        set1.setLineWidth(1.5f);
        set1.setDrawCircles(false);
        set1.setDrawValues(false);
        set1.setFillAlpha(65);
        set1.setFillColor(ColorTemplate.getHoloBlue());
        set1.setHighLightColor(Color.rgb(244, 117, 117));
        set1.setDrawCircleHole(false);
        set1.setMode(LineDataSet.Mode.CUBIC_BEZIER);

        LineData lineData = new LineData(set1);
        chart.setData(lineData);
        chart.invalidate();
    }

    private void setUpMapUI() {
        Button refreshButton = findViewById(R.id.refresh_icon);
        refreshButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                displayBikeStations();
            }
        });
    }

    private void setUpBottomSheet() {
        View bottomSheet = findViewById(R.id.bottom_sheet);
        BottomSheetBehavior bottomSheetBehavior = BottomSheetBehavior.from(bottomSheet);
        bottomSheetBehavior.setState(BottomSheetBehavior.STATE_HIDDEN);

        View routeBottomSheet = findViewById(R.id.route_bottom_sheet);
        bottomSheetBehavior = BottomSheetBehavior.from(routeBottomSheet);
        bottomSheetBehavior.setState(BottomSheetBehavior.STATE_HIDDEN);

        SupportStreetViewPanoramaFragment streetViewPanoramaFragment =
                (SupportStreetViewPanoramaFragment)
                        getSupportFragmentManager().findFragmentById(R.id.streetviewpanorama);
        streetViewPanoramaFragment.getStreetViewPanoramaAsync(
                new OnStreetViewPanoramaReadyCallback() {
                    @Override
                    public void onStreetViewPanoramaReady(StreetViewPanorama panorama) {
                        mStreetViewPanorama = panorama;
                    }
                });
    }

    private void setUpAutocomplete() {
        if (!Places.isInitialized()) {
            Places.initialize(getApplicationContext(), getString(R.string.google_maps_key), Locale.US);
        }

        // Initialize the AutocompleteSupportFragment.
        AutocompleteSupportFragment autocompleteFragment = (AutocompleteSupportFragment)
                getSupportFragmentManager().findFragmentById(R.id.autocomplete_fragment);

        // Specify the types of place data to return.
        autocompleteFragment.setPlaceFields(Arrays.asList(Place.Field.NAME, Place.Field.ADDRESS, Place.Field.LAT_LNG));

        RectangularBounds bounds = RectangularBounds.newInstance(
                new LatLng(53.236989, -6.486053),
                new LatLng(53.445249, -6.016388));
        autocompleteFragment.setLocationRestriction(bounds);

        autocompleteFragment.setOnPlaceSelectedListener(new PlaceSelectionListener() {
            @Override
            public void onPlaceSelected(Place place) {
                LatLng dublin = new LatLng(53.3499, -6.2603);
                mMap.animateCamera(CameraUpdateFactory.newLatLng(dublin));
                mMap.animateCamera(CameraUpdateFactory.zoomTo(13f));
                mClusterManager.clearItems();

                View routeBottomSheet = findViewById(R.id.route_bottom_sheet);
                BottomSheetBehavior bottomSheetBehavior = BottomSheetBehavior.from(routeBottomSheet);
                bottomSheetBehavior.setState(BottomSheetBehavior.STATE_EXPANDED);

                LocationManager locationManager = (LocationManager)
                        getSystemService(Context.LOCATION_SERVICE);
                Criteria criteria = new Criteria();

                if (checkSelfPermission(Manifest.permission.ACCESS_FINE_LOCATION) != PackageManager.PERMISSION_GRANTED && checkSelfPermission(Manifest.permission.ACCESS_COARSE_LOCATION) != PackageManager.PERMISSION_GRANTED) {
                    Log.e("MapsActivity","oof");
                }

                Location location = locationManager.getLastKnownLocation(Objects.requireNonNull(locationManager
                        .getBestProvider(criteria, false)));

                mMap.addMarker(new MarkerOptions().position(new LatLng(53.330667,-6.258590)));
                mMap.addMarker(new MarkerOptions().position(place.getLatLng()));
                String start = "53.330667,-6.258590";
                // String start = + location.getLatitude() + "," + location.getLongitude();

                String end = place.getLatLng().latitude + "," + place.getLatLng().longitude;

                String url = "https://oisin-flask-test.herokuapp.com/?start="+ start + "&end="+end;

                StringRequest stringRequest = getRouteRequest(url);


                queue.add(stringRequest);
            }

            @Override
            public void onError(Status status) {
                // TODO: Handle the error.
                Log.i(".MapsActivity", "An error occurred: " + status);
            }
        });
    }

    private StringRequest getRouteRequest(String url) {
        return new StringRequest(Request.Method.GET, url,
                new Response.Listener<String>() {
                    @Override
                    public void onResponse(String response) {
                        try {
                            for (Polyline line : routeLines) {
                               line.remove();
                            }

                            JSONObject route = new JSONObject(response);

                            JSONObject cycleRoute = route.getJSONObject("cycle_route");
                            JSONObject startWalkingRoute = route.getJSONObject("start_walking_route");
                            JSONObject endWalkingRoute = route.getJSONObject("end_walking_route");

                            routeLines.add(mMap.addPolyline(getCycleLine(cycleRoute)));
                            routeLines.add(mMap.addPolyline(getWalkingRoute(startWalkingRoute)));
                            routeLines.add(mMap.addPolyline(getWalkingRoute(endWalkingRoute)));

                            mClusterManager.addItem(clusterItems.get(route.getString("start_station")));
                            mClusterManager.addItem(clusterItems.get(route.getString("end_station")));
                        } catch (JSONException e) {
                            e.printStackTrace();
                        }
                    }
                }, new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError error) {
                Log.e("RouteActivity", "error with route request");
            }
        });
    }

    private PolylineOptions getCycleLine(JSONObject cycleRoute) throws JSONException {
        String[] coordinates = cycleRoute.getJSONArray("marker").getJSONObject(0)
                .getJSONObject("@attributes").getString("coordinates").split(" ");
        PolylineOptions line = new PolylineOptions();

        LatLngBounds.Builder boundsBuilder = new LatLngBounds.Builder();
        for (String coordinate : coordinates) {
            String longitude = coordinate.split(",")[0];
            String latitude = coordinate.split(",")[1];

            LatLng latLng = new LatLng(Double.parseDouble(latitude), Double.parseDouble(longitude));
            line.add(latLng);
            boundsBuilder.include(latLng);
        }

        mMap.animateCamera(CameraUpdateFactory.newLatLngBounds(boundsBuilder.build(), 300));

        return line.jointType(JointType.ROUND).endCap(new RoundCap()).startCap(new RoundCap()).color(Color.rgb(134, 122, 214));
    }

    private PolylineOptions getWalkingRoute(JSONObject walkingRoute) throws JSONException {
        JSONArray coordinates = walkingRoute.getJSONArray("features").getJSONObject(0)
                .getJSONObject("geometry").getJSONArray("coordinates");

        PolylineOptions line = new PolylineOptions();

        for (int i = 0; i < coordinates.length(); i++) {
            JSONArray array = coordinates.getJSONArray(i);

            String longitude = array.getString(0);
            String latitude = array.getString(1);

            line.add(new LatLng(Double.parseDouble(latitude), Double.parseDouble(longitude)));
        }

        List<PatternItem> pattern = Arrays.asList(new Dot(), new Gap(10));

        return line.pattern(pattern).jointType(JointType.ROUND).endCap(new RoundCap()).startCap(new RoundCap()).color(Color.rgb(134, 122, 214));
    }

    private class StationRenderer extends DefaultClusterRenderer {

        public StationRenderer() {
            super(getApplicationContext(), getMap(), mClusterManager);
        }

        @Override
        protected void onBeforeClusterItemRendered(ClusterItem item, MarkerOptions markerOptions) {
            int availableBikes = Integer.parseInt(item.getSnippet().split(" bikes available")[0].split(" out of ")[0]);

            markerOptions.icon(BitmapDescriptorFactory.fromResource(getResourceForStation(availableBikes)));

            super.onBeforeClusterItemRendered(item, markerOptions);
        }
    }

    private int getResourceForStation(int availableBikes) {

        switch (availableBikes) {
            case 0:
                return R.drawable.zero_bikes_medium;
            case 1:
                return R.drawable.one_bike_medium;
            case 2:
                return R.drawable.two_bikes_medium;
            case 3:
                return R.drawable.three_bikes_medium;
            case 4:
                return R.drawable.four_bikes_medium;
            case 5:
                return R.drawable.five_bikes_medium;
            case 6:
                return R.drawable.six_bikes_medium;
            case 7:
                return R.drawable.seven_bikes_medium;
            case 8:
                return R.drawable.eight_bikes_medium;
            default:
                return R.drawable.nine_plus_bikes_medium;
        }
    }

    private void enableMyLocation() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.ACCESS_FINE_LOCATION)
                == PackageManager.PERMISSION_GRANTED) {
            mMap.setMyLocationEnabled(true);
            mMap.getUiSettings().setMyLocationButtonEnabled(true);
            mMap.getUiSettings().setMapToolbarEnabled(false);
        } else {
            // Show rationale and request permission.
            ActivityCompat.requestPermissions(this,
                    new String[]{android.Manifest.permission.ACCESS_FINE_LOCATION},
                    PERMISSIONS_REQUEST_ACCESS_FINE_LOCATION);
        }
    }

    private void displayBikeStations() {
        String url = "https://api.jcdecaux.com/vls/v1/stations?contract=dublin&apiKey=6e5c2a98e60a3336ecaede8f8c8688da25144692";

        // Request a string response from the provided URL.
        StringRequest stringRequest = new StringRequest(Request.Method.GET, url,
                new Response.Listener<String>() {
                    @Override
                    public void onResponse(String response) {
                        mMap.clear();
                        mClusterManager.clearItems();

                        try {
                            JSONArray stations = new JSONArray(response);
                            List<StationClusterItem> items = new ArrayList<>();

                            for (int i = 0; i < stations.length(); i++) {
                                JSONObject station = stations.getJSONObject(i);
                                StationClusterItem stationClusterItem = new StationClusterItem(station.getJSONObject("position").getDouble("lat"),
                                        station.getJSONObject("position").getDouble("lng"),
                                        station.getString("address"),
                                        station.getInt("available_bikes") + " out of " + station.getInt("bike_stands") + " bikes available");

                                items.add(stationClusterItem);
                                clusterItems.put(stationClusterItem.getTitle(), stationClusterItem);
                            }

                            mClusterManager.addItems(items);
                            mClusterManager.cluster();
                        } catch (JSONException e) {
                            e.printStackTrace();
                        }
                    }
                }, new Response.ErrorListener() {
            @Override
            public void onErrorResponse(VolleyError error) {
            }
        });

        queue.add(stringRequest);
    }

    public GoogleMap getMap() {
        return mMap;
    }

    @Override
    public void onMapReady(final GoogleMap map) {
        map.setOnMarkerClickListener(this);

        mMap = map;

        mClusterManager = new ClusterManager<>(this, map);
        mClusterManager.setRenderer(new StationRenderer());
        map.setOnCameraIdleListener(mClusterManager);


        map.setMapStyle(new MapStyleOptions(getResources()
                .getString(R.string.map_style)));

        displayBikeStations();

        // Add a marker in Dublin and move the camera
        LatLng dublin = new LatLng(53.3498, -6.2603);
        map.moveCamera(CameraUpdateFactory.zoomTo(16f));
        map.moveCamera(CameraUpdateFactory.newLatLng(dublin));

        enableMyLocation();
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, String[] permissions, int[] grantResults) {
        if (requestCode == PERMISSIONS_REQUEST_ACCESS_FINE_LOCATION) {
            if (permissions.length == 1 &&
                    permissions[0].equals(Manifest.permission.ACCESS_FINE_LOCATION) &&
                    grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                mMap.setMyLocationEnabled(true);
                mMap.getUiSettings().setMyLocationButtonEnabled(true);
                mMap.getUiSettings().setMapToolbarEnabled(true);
            } else {
                //todo Permission was denied. Display an error message.
            }
        }
    }

    @Override
    public boolean onMarkerClick(final Marker marker) {
        if (marker.getTitle() == null) return false;

        View bottomSheet = findViewById(R.id.bottom_sheet);
        BottomSheetBehavior bottomSheetBehavior = BottomSheetBehavior.from(bottomSheet);

        TextView text = findViewById(R.id.bottom_sheet_title);
        text.setText(marker.getTitle());

        text = findViewById(R.id.bottom_sheet_byline);
        text.setText(marker.getSnippet());

        CameraUpdate yourLocation = CameraUpdateFactory.newLatLngZoom(marker.getPosition(), mMap.getCameraPosition().zoom);
        mMap.animateCamera(yourLocation, 300, null);

        mStreetViewPanorama.setPosition(marker.getPosition());

        bottomSheetBehavior.setState(BottomSheetBehavior.STATE_COLLAPSED);

        return true;
    }
}
