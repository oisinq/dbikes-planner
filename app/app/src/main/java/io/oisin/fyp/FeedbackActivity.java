package io.oisin.fyp;

import android.content.Intent;
import android.os.Bundle;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.LinearLayout;
import android.widget.RadioButton;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.appcompat.widget.Toolbar;

import com.android.volley.Request;
import com.android.volley.RequestQueue;
import com.android.volley.Response;
import com.android.volley.VolleyError;
import com.android.volley.VolleyLog;
import com.android.volley.toolbox.JsonObjectRequest;
import com.android.volley.toolbox.Volley;
import com.google.android.material.slider.Slider;

import org.json.JSONException;
import org.json.JSONObject;

public class FeedbackActivity extends AppCompatActivity {
    JSONObject route;
    String startStation;
    String endStation;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_feedback);

        try {
            route = new JSONObject(getIntent().getStringExtra("route"));
            startStation = route.getString("start_station");
            endStation = route.getString("end_station");

            TextView startQuestion = findViewById(R.id.feedback_start_question);
            TextView endQuestion = findViewById(R.id.feedback_end_question);

            startQuestion.setText("Was there a queue for bikes at the " + startStation + " station?");
            endQuestion.setText("Was there a queue for spaces at the " + endStation + " station?");
        } catch (JSONException e) {
            e.printStackTrace();
        }

        Toolbar myToolbar = findViewById(R.id.my_toolbar);
        setSupportActionBar(myToolbar);

        final RadioButton startYesButton = findViewById(R.id.feedback_start_yes);
        RadioButton startNoButton = findViewById(R.id.feedback_start_no);

        startYesButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                LinearLayout question = findViewById(R.id.feedback_start_group);
                question.setVisibility(View.VISIBLE);
            }
        });

        startNoButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                LinearLayout question = findViewById(R.id.feedback_start_group);
                question.setVisibility(View.GONE);
            }
        });

        final RadioButton endYesButton = findViewById(R.id.feedback_end_yes);
        RadioButton endNoButton = findViewById(R.id.feedback_end_no);

        endYesButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                LinearLayout question = findViewById(R.id.feedback_end_group);
                question.setVisibility(View.VISIBLE);
            }
        });

        endNoButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                LinearLayout question = findViewById(R.id.feedback_end_group);
                question.setVisibility(View.GONE);
            }
        });

        final Slider startSlider = findViewById(R.id.feedback_start_wait_time);
        startSlider.addOnChangeListener(new Slider.OnChangeListener(){

            @Override
            public void onValueChange(@NonNull Slider slider, float value, boolean fromUser) {
                TextView textView = findViewById(R.id.start_slider_minutes);

                textView.setText((int) value + " minutes");
            }
        });

        final Slider endSlider = findViewById(R.id.feedback_end_wait_time);
        endSlider.addOnChangeListener(new Slider.OnChangeListener(){

            @Override
            public void onValueChange(@NonNull Slider slider, float value, boolean fromUser) {
                TextView textView = findViewById(R.id.end_slider_minutes);

                textView.setText((int) value + " minutes");
            }
        });

        Button submitButton = findViewById(R.id.feedback_submit_button);
        submitButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                final JSONObject result = new JSONObject();

                try {
                    if (startYesButton.isChecked()) {
                        result.put("start_wait", startSlider.getValue());
                    }

                    if (endYesButton.isChecked()) {
                        result.put("end_wait", endSlider.getValue());
                    }

                    result.put("id", route.getString("id"));

                    RequestQueue queue = Volley.newRequestQueue(getApplicationContext());

                    JsonObjectRequest request = generateJSONRequest(result);

                    queue.add(request);

                    Intent intent = new Intent(getApplicationContext(), MapsActivity.class);
                    intent.putExtra("feedbackSubmitted", true);

                    startActivity(intent);
                } catch (JSONException e) {
                    e.printStackTrace();
                }
            }
        });
    }

    private JsonObjectRequest generateJSONRequest(final JSONObject result) throws JSONException {
        String url ="https://dbikes-planner.appspot.com/feedback/" + route.getString("id");

        url = url.replace(" ", "%20");

        return new JsonObjectRequest(Request.Method.POST,
                url, result,
                new Response.Listener<JSONObject>() {

                    @Override
                    public void onResponse(JSONObject response) {
                        Log.d("JSONPost", response.toString());
                        //pDialog.hide();
                    }
                }, new Response.ErrorListener() {

            @Override
            public void onErrorResponse(VolleyError error) {
                VolleyLog.d("JSONPost", "Error: " + error.getMessage());
                //pDialog.hide();
            }
        });
    }
}
